import geopandas as gpd
from typing import Optional
from .species_resolver import SpeciesNameResolver
from .sources import USGSGAPSource


# Initialize default components
_resolver = SpeciesNameResolver()
_default_source = USGSGAPSource()


def get_species_range(species_name: str, source: str = "usgs_gap") -> Optional[gpd.GeoDataFrame]:
    """Get species range map as a GeoPandas GeoDataFrame.
    
    Args:
        species_name: Common or scientific name of the species
        source: Data source to use (default: "usgs_gap")
        
    Returns:
        GeoDataFrame with species range geometry or None if not found
        
    Raises:
        ValueError: If the source is not supported
        NotImplementedError: If the source is not yet implemented
    """
    # Validate source first
    if source not in ["usgs_gap"]:
        raise ValueError(f"Unsupported source: {source}")
    
    # First, try searching with the original species name
    print(f"Searching for species range using original name: '{species_name}'")
    
    if source == "usgs_gap":
        try:
            # Try with original name first
            result = _default_source.get_species_range(species_name)
            if result is not None:
                print(f"Found species data using original name: '{species_name}'")
                return result
                
            # If no results with original name, try name resolution
            print(f"No results found with original name, attempting name resolution...")
            species_info = _resolver.resolve_name(species_name)
            
            if not species_info:
                print(f"Could not resolve species name: {species_name}")
                return None
            
            scientific_name = species_info["scientific_name"]
            print(f"Resolved '{species_name}' to '{scientific_name}'")
            
            # Try again with the scientific name
            if scientific_name != species_name:  # Only search again if names are different
                print(f"Searching again with scientific name: '{scientific_name}'")
                result = _default_source.get_species_range(scientific_name)
                if result is not None:
                    print(f"Found species data using scientific name: '{scientific_name}'")
                    # Update the result to include both names
                    result['original_query'] = species_name
                    result['common_name'] = species_info.get("common_name", "")
                    return result
            
            print(f"No species data found for '{species_name}' or '{scientific_name}'")
            return None
            
        except NotImplementedError as e:
            raise ValueError(f"USGS GAP source implementation error: {e}")


def list_available_sources() -> list:
    """List available range data sources.
    
    Returns:
        List of available source names
    """
    return ["usgs_gap"]


def search_species(query: str, source: str = "usgs_gap") -> list:
    """Search for species matching the query.
    
    Args:
        query: Search term (common or scientific name)
        source: Data source to search (default: "usgs_gap")
        
    Returns:
        List of matching species information
    """
    # Use the resolver to find species matches
    species_info = _resolver.resolve_name(query)
    
    if species_info:
        return [species_info]
    else:
        return []