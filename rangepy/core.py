import geopandas as gpd
from typing import Optional, Literal
from .species_resolver import SpeciesNameResolver
from .sources import USGSGAPSource
import requests
from shapely.geometry import box
from functools import cache


# Initialize default components
_resolver = SpeciesNameResolver()
_default_source = USGSGAPSource()


@cache
def _get_admin_boundaries(admin_level: str) -> gpd.GeoDataFrame:
    """Get administrative boundaries from Natural Earth data, with caching.

    Args:
        admin_level: Either 'admin0' (countries) or 'admin1' (states/provinces)
        bounds: Optional tuple (minx, miny, maxx, maxy) to filter boundaries

    Returns:
        GeoDataFrame with administrative boundaries
    """
    if admin_level == 'admin0':
        # Natural Earth countries (1:110m resolution)
        file_path = "https://naciscdn.org/naturalearth/110m/cultural/ne_110m_admin_0_countries.zip"
    elif admin_level == 'admin1':
        # Natural Earth states/provinces (1:10m resolution)
        file_path = "https://naciscdn.org/naturalearth/10m/cultural/ne_10m_admin_1_states_provinces.zip"
    else:
        raise ValueError(f"Unsupported admin_level: {admin_level}. Use 'admin0' or 'admin1'.")

    # Download and cache the file using pooch, then read it
    try:
        admin_gdf = gpd.read_file(file_path)
    except (requests.exceptions.RequestException, Exception) as e:
        print(f"Could not download boundary file: {e}")
        raise IOError(f"Failed to download or read {admin_level} boundaries.") from e

    return admin_gdf


def get_species_range(
    species_name: str,
    source: str = "usgs_gap",
    admin_level: Optional[Literal['admin0', 'admin1']] = None
) -> Optional[gpd.GeoDataFrame]:
    """Get species range map as a GeoPandas GeoDataFrame.

    Args:
        species_name: Common or scientific name of the species
        source: Data source to use (default: "usgs_gap")
        admin_level: Optional. If provided, aggregates range to administrative boundaries.
                    'admin0' for countries, 'admin1' for states/provinces.
                    Any country/state that intersects with the original range will be
                    included in its entirety in the returned range map.

    Returns:
        GeoDataFrame with species range geometry or None if not found.
        If admin_level is specified, returns administrative boundaries that intersect
        with the original species range.

    Raises:
        ValueError: If the source is not supported or admin_level is invalid
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
            else:
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
                    else:
                        print(f"No species data found for '{species_name}' or '{scientific_name}'")
                        return None
                else:
                    print(f"No species data found for '{species_name}'")
                    return None

            # If admin_level is specified, aggregate to administrative boundaries
            if admin_level is not None and result is not None:
                print(f"Aggregating range to {admin_level} boundaries...")

                # Ensure consistent CRS for intersection
                original_crs = result.crs
                result_wgs84 = result.to_crs(epsg=4326)

                # Get bounds of species range to filter admin boundaries
                bounds = result_wgs84.total_bounds

                # Get administrative boundaries
                admin_gdf = _get_admin_boundaries(admin_level)
                admin_gdf_wgs84 = admin_gdf.to_crs(epsg=4326)

                # Find all admin boundaries that intersect with species range
                try:
                    # Try newer GeoPandas method first
                    range_union = result_wgs84.union_all()
                except AttributeError:
                    # Fall back to deprecated unary_union for older versions
                    range_union = result_wgs84.unary_union
                intersecting = admin_gdf_wgs84[admin_gdf_wgs84.intersects(range_union)]

                if len(intersecting) == 0:
                    print(f"Warning: No {admin_level} boundaries intersect with species range")
                    return result

                print(f"Found {len(intersecting)} {admin_level} boundaries intersecting with species range")

                # Transform back to original CRS if needed
                if original_crs is not None:
                    intersecting = intersecting.to_crs(original_crs)

                return intersecting

            return result
            
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