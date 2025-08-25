import pytest
from unittest.mock import patch, MagicMock
import requests
from rangepy.species_resolver import SpeciesNameResolver


class TestSpeciesNameResolver:
    """Test cases for the species name resolver."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.resolver = SpeciesNameResolver()
    
    @patch('rangepy.species_resolver.requests.get')
    def test_resolve_name_success(self, mock_get):
        """Test successful species name resolution."""
        # Mock successful API response
        mock_response = MagicMock()
        mock_response.raise_for_status.return_value = None
        mock_response.json.return_value = {
            "matchType": "EXACT",
            "canonicalName": "Turdus migratorius",
            "vernacularName": "American Robin",
            "kingdom": "Animalia",
            "phylum": "Chordata",
            "class": "Aves",
            "order": "Passeriformes",
            "family": "Turdidae",
            "genus": "Turdus",
            "species": "migratorius",
            "confidence": 100
        }
        mock_get.return_value = mock_response
        
        # Test the function
        result = self.resolver.resolve_name("American Robin")
        
        # Verify the result
        assert result is not None
        assert result["scientific_name"] == "Turdus migratorius"
        assert result["common_name"] == "American Robin"
        assert result["kingdom"] == "Animalia"
        assert result["confidence"] == 100
        
        # Verify API was called correctly
        mock_get.assert_called_once()
        call_args = mock_get.call_args
        assert "name" in call_args[1]["params"]
        assert call_args[1]["params"]["name"] == "American Robin"
    
    @patch('rangepy.species_resolver.requests.get')
    def test_resolve_name_no_match(self, mock_get):
        """Test species name resolution with no match."""
        # Mock API response with no match
        mock_response = MagicMock()
        mock_response.raise_for_status.return_value = None
        mock_response.json.return_value = {
            "matchType": "NONE"
        }
        mock_get.return_value = mock_response
        
        # Test the function
        result = self.resolver.resolve_name("Invalid Species")
        
        # Verify the result
        assert result is None
    
    @patch('rangepy.species_resolver.requests.get')
    def test_resolve_name_api_error(self, mock_get):
        """Test species name resolution with API error."""
        # Mock API error
        mock_get.side_effect = requests.RequestException("API Error")
        
        # Test the function
        result = self.resolver.resolve_name("American Robin")
        
        # Verify the result
        assert result is None
    
    @patch('rangepy.species_resolver.requests.get')
    def test_get_scientific_name(self, mock_get):
        """Test getting scientific name directly."""
        # Mock successful API response
        mock_response = MagicMock()
        mock_response.raise_for_status.return_value = None
        mock_response.json.return_value = {
            "matchType": "EXACT",
            "canonicalName": "Turdus migratorius",
            "vernacularName": "American Robin"
        }
        mock_get.return_value = mock_response
        
        # Test the function
        result = self.resolver.get_scientific_name("American Robin")
        
        # Verify the result
        assert result == "Turdus migratorius"
    
    @patch('rangepy.species_resolver.requests.get')
    def test_get_scientific_name_not_found(self, mock_get):
        """Test getting scientific name for non-existent species."""
        # Mock API response with no match
        mock_response = MagicMock()
        mock_response.raise_for_status.return_value = None
        mock_response.json.return_value = {"matchType": "NONE"}
        mock_get.return_value = mock_response
        
        # Test the function
        result = self.resolver.get_scientific_name("Invalid Species")
        
        # Verify the result
        assert result is None