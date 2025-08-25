from abc import ABC, abstractmethod
import geopandas as gpd
import requests
import pandas as pd
from typing import Optional, Dict, Any, List
import json
import tempfile
import os
import zipfile
import shutil
from pathlib import Path


class RangeSource(ABC):
    """Abstract base class for species range data sources."""
    
    @abstractmethod
    def get_species_range(self, species_name: str) -> Optional[gpd.GeoDataFrame]:
        """Get species range as a GeoDataFrame.
        
        Args:
            species_name: Common or scientific name of species
            
        Returns:
            GeoDataFrame with species range or None if not found
        """
        pass
    
    @abstractmethod
    def search_species(self, query: str) -> list:
        """Search for species matching the query.
        
        Args:
            query: Search term (common or scientific name)
            
        Returns:
            List of matching species information
        """
        pass


class ScienceBaseGAPSource(RangeSource):
    """USGS GAP Analysis Program species range source using ScienceBase."""
    
    def __init__(self):
        self.gap_item_id = "5951527de4b062508e3b1e79"  # GAP species range maps item ID
        self.sciencebase_base_url = "https://www.sciencebase.gov"
        
    def _get_sciencebase_session(self):
        """Create and return a ScienceBase session."""
        try:
            import sciencebasepy as sb
            session = sb.SbSession()
            return session
        except ImportError:
            print("sciencebasepy not installed. Install with: pip install sciencebasepy")
            return None
    
    def _search_gap_species(self, species_name: str) -> List[Dict]:
        """Search for species in the GAP database via ScienceBase."""
        session = self._get_sciencebase_session()
        if not session:
            return []
            
        try:
            # Search for items related to the species in the GAP dataset
            search_params = {
                'q': species_name,
                'parentId': self.gap_item_id,
                'fields': 'title,summary,tags,facets,files',
                'max': 20
            }
            
            results = session.find_items(search_params)
            species_items = []
            
            if results and 'items' in results:
                for item in results['items']:
                    # Look for items that contain species range data
                    if any(keyword in item.get('title', '').lower() 
                          for keyword in ['range', 'habitat', 'distribution']):
                        species_items.append({
                            'id': item.get('id'),
                            'title': item.get('title', ''),
                            'summary': item.get('summary', ''),
                            'tags': item.get('tags', [])
                        })
            
            return species_items
            
        except Exception as e:
            print(f"Error searching ScienceBase: {e}")
            return []
    
    def _download_species_files(self, item_id: str) -> List[Dict]:
        """Get information about files associated with a species item."""
        session = self._get_sciencebase_session()
        if not session:
            return []
            
        try:
            item = session.get_item(item_id)
            files = item.get('files', [])
            
            available_files = []
            for file_info in files:
                # Look for geospatial files (shapefiles, GeoJSON, etc.)
                name = file_info.get('name', '').lower()
                if any(ext in name for ext in ['.shp', '.geojson', '.json', '.zip']):
                    # Extract file information (no actual download for now)
                    available_files.append({
                        'name': file_info['name'],
                        'url': file_info.get('url', ''),
                        'download_url': file_info.get('downloadUri', ''),
                        'type': file_info.get('contentType', ''),
                        'size': file_info.get('size', 0),
                        'checksum': file_info.get('checksum', {})
                    })
            
            return available_files
            
        except Exception as e:
            print(f"Error accessing files for item {item_id}: {e}")
            return []
    
    def _download_and_process_range_files(self, files: List[Dict], temp_dir: str) -> Optional[gpd.GeoDataFrame]:
        """Download and process range map files to create a GeoDataFrame."""
        session = self._get_sciencebase_session()
        if not session:
            return None
            
        for file_info in files:
            try:
                if not file_info.get('url') and not file_info.get('download_url'):
                    print(f"No download URL available for file: {file_info['name']}")
                    continue
                
                # Use the available URL
                download_url = file_info.get('url') or file_info.get('download_url')
                local_filename = file_info['name']
                local_path = os.path.join(temp_dir, local_filename)
                
                print(f"Downloading {local_filename}...")
                session.download_file(download_url, local_filename, destination=temp_dir)
                
                # Process the downloaded file
                gdf = self._process_geospatial_file(local_path, file_info)
                if gdf is not None:
                    return gdf
                    
            except Exception as e:
                print(f"Error downloading/processing file {file_info['name']}: {e}")
                continue
        
        return None
    
    def _process_geospatial_file(self, file_path: str, file_info: Dict) -> Optional[gpd.GeoDataFrame]:
        """Process a downloaded geospatial file into a GeoDataFrame."""
        try:
            path_obj = Path(file_path)
            
            if not path_obj.exists():
                print(f"Downloaded file not found: {path_obj}")
                return None
            
            # Handle different file types
            if path_obj.suffix.lower() == '.zip':
                return self._process_zip_file(path_obj, file_info)
            elif path_obj.suffix.lower() == '.geojson':
                return gpd.read_file(file_path)
            elif path_obj.suffix.lower() == '.shp':
                return gpd.read_file(file_path)
            else:
                print(f"Unsupported file format: {path_obj.suffix}")
                return None
                
        except Exception as e:
            print(f"Error processing geospatial file {file_path}: {e}")
            return None
    
    def _process_zip_file(self, zip_path: Path, file_info: Dict) -> Optional[gpd.GeoDataFrame]:
        """Extract and process a ZIP file containing geospatial data."""
        try:
            extract_dir = zip_path.parent / f"{zip_path.stem}_extracted"
            extract_dir.mkdir(exist_ok=True)
            
            # Extract the ZIP file
            with zipfile.ZipFile(zip_path, 'r') as zip_ref:
                zip_ref.extractall(extract_dir)
            
            # Look for shapefiles or GeoJSON files in the extracted content
            for extracted_file in extract_dir.rglob('*'):
                if extracted_file.suffix.lower() in ['.shp', '.geojson']:
                    print(f"Processing extracted file: {extracted_file.name}")
                    gdf = gpd.read_file(extracted_file)
                    
                    # Add metadata from the original file info
                    gdf['source_file'] = file_info['name']
                    gdf['download_url'] = file_info.get('url', '')
                    gdf['file_size'] = file_info.get('size', 0)
                    
                    return gdf
            
            print(f"No geospatial files found in ZIP: {zip_path}")
            return None
            
        except Exception as e:
            print(f"Error processing ZIP file {zip_path}: {e}")
            return None
    
    def get_species_range(self, species_name: str) -> Optional[gpd.GeoDataFrame]:
        """Get species range from ScienceBase GAP Analysis data."""
        temp_dir = None
        try:
            # Search for the species in ScienceBase
            species_items = self._search_gap_species(species_name)
            
            if not species_items:
                raise ValueError(f"No species data found in ScienceBase for: {species_name}")
            
            # Try to get geospatial data from the first matching item
            first_item = species_items[0]
            files = self._download_species_files(first_item['id'])
            
            if not files:
                raise ValueError(f"No geospatial files found for species: {species_name}")
            
            print(f"Found {len(files)} geospatial file(s) for {species_name}")
            
            # Create temporary directory for downloads
            temp_dir = tempfile.mkdtemp(prefix=f"rangepy_{species_name.replace(' ', '_')}_")
            
            # Download and process the actual range data
            range_gdf = self._download_and_process_range_files(files, temp_dir)
            
            if range_gdf is None:
                raise ValueError(f"Failed to download or process range data for species: {species_name}")
            
            # Add species metadata to the GeoDataFrame
            range_gdf['species_name'] = species_name
            range_gdf['source'] = 'sciencebase_gap'
            range_gdf['item_id'] = first_item['id']
            range_gdf['title'] = first_item['title']
            
            print(f"Successfully loaded range map for {species_name} with {len(range_gdf)} features")
            
            # Ensure we have a proper CRS
            if range_gdf.crs is None:
                print("No CRS found in data, assuming EPSG:4326 (WGS84)")
                range_gdf.set_crs('EPSG:4326', inplace=True)
            
            return range_gdf
            
        except Exception as e:
            print(f"Error retrieving species range from ScienceBase: {e}")
            raise
        finally:
            # Clean up temporary files
            if temp_dir and os.path.exists(temp_dir):
                try:
                    shutil.rmtree(temp_dir)
                    print(f"Cleaned up temporary directory: {temp_dir}")
                except Exception as cleanup_error:
                    print(f"Warning: Failed to clean up temporary directory {temp_dir}: {cleanup_error}")
    
    def search_species(self, query: str) -> list:
        """Search for species in ScienceBase GAP database."""
        try:
            species_items = self._search_gap_species(query)
            return [{'title': item['title'], 'id': item['id'], 'summary': item['summary']} 
                   for item in species_items]
        except Exception as e:
            print(f"Error searching species in ScienceBase: {e}")
            return []


# Keep the old class name for backward compatibility but use the new implementation
USGSGAPSource = ScienceBaseGAPSource