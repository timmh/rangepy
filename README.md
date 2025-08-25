# RangePy

A minimal Python library for retrieving species range maps as GeoPandas dataframes. For now, this library is limited to the Contiguous United States.

## Installation

```bash
pip install -e .
```

## Requirements

- geopandas
- sciencebasepy
- requests

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
- USGS ScienceBase species range maps via ScienceBase API

## License

MIT License