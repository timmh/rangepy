import requests
from typing import Optional, Dict, Any


class SpeciesNameResolver:
    """Resolves common names to scientific names using taxonomic databases."""
    
    def __init__(self):
        # Using GBIF API for name resolution
        self.gbif_api_base = "https://api.gbif.org/v1"
        
    def resolve_name(self, name: str) -> Optional[Dict[str, Any]]:
        """Resolve a species name to standardized taxonomic information.
        
        Args:
            name: Common or scientific name
            
        Returns:
            Dict with species information or None if not found
        """
        try:
            # Try to match the name using GBIF species match API
            url = f"{self.gbif_api_base}/species/match"
            params = {"name": name}
            
            response = requests.get(url, params=params, timeout=10)
            response.raise_for_status()
            
            data = response.json()

            print(data)
            
            # Check if we got a good match
            if data.get("matchType") in ["EXACT", "FUZZY"] and data.get("canonicalName"):
                return {
                    "scientific_name": data.get("canonicalName"),
                    "common_name": data.get("vernacularName", ""),
                    "kingdom": data.get("kingdom", ""),
                    "phylum": data.get("phylum", ""),
                    "class": data.get("class", ""),
                    "order": data.get("order", ""),
                    "family": data.get("family", ""),
                    "genus": data.get("genus", ""),
                    "species": data.get("species", ""),
                    "confidence": data.get("confidence", 0)
                }
                
        except Exception as e:
            print(f"Error resolving species name '{name}': {e}")
            
        return None
    
    def get_scientific_name(self, name: str) -> Optional[str]:
        """Get the scientific name for a given common or scientific name.
        
        Args:
            name: Common or scientific name
            
        Returns:
            Scientific name or None if not found
        """
        result = self.resolve_name(name)
        return result["scientific_name"] if result else None