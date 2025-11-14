# RangePy

A minimal Python library for retrieving species range maps as GeoPandas dataframes. For now, this library is limited to the Contiguous United States and species range maps from the USGS (see [Data Sources](#data-sources) for details).

## Installation

```bash
pip install git+https://github.com/timmh/rangepy.git
```

## Usage

```python
import rangepy

# Get range map for a species (accepts common or scientific names)
range_df = rangepy.get_species_range("American Robin")
# or
range_df = rangepy.get_species_range("Turdus migratorius")

# The returned object is a GeoPandas GeoDataFrame
print(range_df.head())
```

## Data Sources

Currently supports:
- [USGS ScienceBase species range maps via ScienceBase API](https://www.sciencebase.gov/catalog/item/5951527de4b062508e3b1e79)

## License

This project is licensed under the MIT License - see the LICENSE file for details.