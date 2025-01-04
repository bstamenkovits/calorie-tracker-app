import os
import pandas as pd

class LocalCacheInterface:

    cache_path = "cache/local"
    empty_dfs = {
        "new_recipe_info": pd.DataFrame(columns=["description"]),
        "new_recipe_tags": pd.DataFrame(columns=["tag"]),
        "new_recipe_ingredients": pd.DataFrame(columns=["ingredient", "quantity", "serving"]),
        "new_recipe_instructions": pd.DataFrame(columns=["instruction"]),
    }

    def __init__(self):
        pass

    def load_from_local_cache(self, sheet_name: str) -> pd.DataFrame:
        file_path = f"{self.cache_path}/{sheet_name}.csv"
        if not os.path.exists(file_path):
            return self.empty_dfs[sheet_name]
        return pd.read_csv(file_path)

    def update_local_cache(self, sheet_name: str, df: pd.DataFrame) -> None:
        """
        Update data in local cache with new data.

        Args:
            sheet_name (str): The name of the sheet in the local cache
            df (pd.DataFrame): The updated data (old data + new data)
                to be stored in the local cache
        """
        file_path = f"{self.cache_path}/{sheet_name}.csv"
        df.to_csv(file_path, index=False)

    def clear_local_cache(self, sheet_name: str) -> None:
        """
        Remove a sheet in the local cache.

        Args:
            sheet_name (str): The name of the sheet in the local cache to be removed
        """
        file_path = f"{self.cache_path}/{sheet_name}.csv"
        if os.path.exists(file_path):
            os.remove(file_path)

    def clear_cache(self):
        """
        Clear the cache of downloaded Google Sheets data
        """
        for file in os.listdir(self.cache_path):
            if file.endswith(".csv"):
                os.remove(f"{self.cache_path}/{file}")
