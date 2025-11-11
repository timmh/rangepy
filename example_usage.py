#!/usr/bin/env python3
"""
Example usage of the rangepy library.

This script demonstrates how to use rangepy to retrieve species range maps.
"""

import rangepy

def main():
    print("RangePy Example Usage")
    print("=" * 50)
    
    # List available data sources
    print("Available sources:", rangepy.list_available_sources())
    
    species_examples = [
        "American Tree Sparrow",
        "American beaver",
        "Castor canadensis",
        "Pronghorn",
        "Antilocapra americana",
        "Gray Wolf",
        "American black bear",
        "Bobcat",
        "Coyote",
        "Douglas squirrel",
        "Eastern chipmunk",
        "Eastern cottontail",
        "Eastern fox squirrel",
        "Eeastern gray squirrel",
        "Mule deer",
        "Nine-banded armadillo",
        "Northern raccoon",
        "Red fox",
        "Virginia opossum",
        "Western gray squirrel",
        "White-tailed antelope squirrel",
        "White-tailed deer",
    ]

    for admin_level in [None, "admin1", "admin0"]:
        for species in species_examples:
            print(f"\nTrying to get range for: {species}")
            
            # Search for the species first
            search_results = rangepy.search_species(species)
            print(f"Search results: {len(search_results)} found")
            
            # Get the range map
            try:
                range_df = rangepy.get_species_range(species, admin_level="admin1")
                if range_df is not None:
                    print(f"Successfully retrieved range data!")
                    print(f"DataFrame shape: {range_df.shape}")
                    print(f"Columns: {list(range_df.columns)}")
                    print(f"CRS: {range_df.crs}")
                    print("Sample data:")
                    print(range_df.head())
                    # Plot the range map
                    try:
                        import os
                        import matplotlib.pyplot as plt
                        import contextily as ctx

                        # Create a plot
                        fig, ax = plt.subplots(figsize=(10, 10))

                        # Plot the species range, reprojecting to Web Mercator (EPSG:3857) for the basemap
                        range_df.to_crs(epsg=3857).plot(ax=ax, alpha=0.5, edgecolor='k', facecolor='red')

                        # Add a basemap from contextily
                        ctx.add_basemap(ax, source=ctx.providers.OpenStreetMap.Mapnik)

                        # Customize and show the plot
                        ax.set_title(f"Range Map for {species}")
                        ax.set_axis_off()
                        plt.tight_layout()
                        os.makedirs("figures", exist_ok=True)
                        plt.savefig(f"figures/{species.replace(' ', '_')}_{str(admin_level)}_range_map.png", bbox_inches='tight', dpi=300)
                        plt.show()
                        plt.close()

                    except ImportError:
                        print("\nPlotting libraries not found. Please install matplotlib and contextily to see the map.")
                    except Exception as plot_error:
                        print(f"\nAn error occurred during plotting: {plot_error}")
                else:
                    print("No range data found")
            except Exception as e:
                print(f"Error retrieving range: {e}")
            
            print("-" * 30)

if __name__ == "__main__":
    main()