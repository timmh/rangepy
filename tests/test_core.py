import pytest
import geopandas as gpd
from unittest.mock import patch, MagicMock
from rangepy.core import get_species_range, list_available_sources, search_species


class TestCore:
    """Test cases for the core rangepy functionality."""
    
    def test_list_available_sources(self):
        """Test that available sources are returned."""
        sources = list_available_sources()
        assert isinstance(sources, list)
        assert "usgs_gap" in sources
    
    @patch('rangepy.core._resolver.resolve_name')
    def test_get_species_range_with_valid_species(self, mock_resolve):
        """Test getting species range with a valid species name."""
        # Mock the species resolver
        mock_resolve.return_value = {
            "scientific_name": "Turdus migratorius",
            "common_name": "American Robin",
            "kingdom": "Animalia"
        }
        
        # Test the function
        result = get_species_range("American Robin")
        
        # Verify the result
        assert isinstance(result, gpd.GeoDataFrame)
        assert len(result) > 0
        assert "species_name" in result.columns
        assert "geometry" in result.columns
        # Now it should use the original name first if found
        assert result["species_name"].iloc[0] == "American Robin"
    
    @patch('rangepy.core._resolver.resolve_name')
    def test_get_species_range_with_invalid_species(self, mock_resolve):
        """Test getting species range with an invalid species name."""
        # Mock the species resolver to return None
        mock_resolve.return_value = None
        
        # Test the function - should now raise ValueError
        with pytest.raises(ValueError, match="No species data found in ScienceBase"):
            get_species_range("Invalid Species Name")
    
    def test_get_species_range_with_invalid_source(self):
        """Test getting species range with an invalid source."""
        with pytest.raises(ValueError, match="Unsupported source"):
            get_species_range("American Robin", source="invalid_source")
    
    @patch('rangepy.core._resolver.resolve_name')
    def test_search_species(self, mock_resolve):
        """Test species search functionality."""
        # Mock the species resolver
        mock_resolve.return_value = {
            "scientific_name": "Turdus migratorius",
            "common_name": "American Robin",
            "kingdom": "Animalia"
        }
        
        # Test the function
        result = search_species("robin")
        
        # Verify the result
        assert isinstance(result, list)
        assert len(result) == 1
        assert result[0]["scientific_name"] == "Turdus migratorius"
    
    @patch('rangepy.core._resolver.resolve_name')
    def test_search_species_no_results(self, mock_resolve):
        """Test species search with no results."""
        # Mock the species resolver to return None
        mock_resolve.return_value = None
        
        # Test the function
        result = search_species("nonexistent species")
        
        # Verify the result
        assert isinstance(result, list)
        assert len(result) == 0