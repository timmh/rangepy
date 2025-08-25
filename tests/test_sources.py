import pytest
from unittest.mock import patch
from rangepy.sources import RangeSource, USGSGAPSource


class TestRangeSource:
    """Test cases for the abstract RangeSource class."""
    
    def test_abstract_class_cannot_be_instantiated(self):
        """Test that the abstract RangeSource class cannot be instantiated."""
        with pytest.raises(TypeError):
            RangeSource()


class TestUSGSGAPSource:
    """Test cases for the USGS GAP source."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.source = USGSGAPSource()
    
    def test_initialization(self):
        """Test that the source initializes correctly."""
        assert self.source.gap_item_id == "5951527de4b062508e3b1e79"
        assert self.source.sciencebase_base_url == "https://www.sciencebase.gov"
    
    @patch('rangepy.sources.ScienceBaseGAPSource._get_sciencebase_session')
    def test_get_species_range_no_session(self, mock_get_session):
        """Test get_species_range when ScienceBase session cannot be created."""
        mock_get_session.return_value = None
        # Should raise ValueError when no session can be created
        with pytest.raises(ValueError, match="No species data found in ScienceBase"):
            self.source.get_species_range("Turdus migratorius")
    
    @patch('rangepy.sources.ScienceBaseGAPSource._get_sciencebase_session')
    def test_search_species_no_session(self, mock_get_session):
        """Test search_species when ScienceBase session cannot be created."""
        mock_get_session.return_value = None
        result = self.source.search_species("robin")
        assert result == []