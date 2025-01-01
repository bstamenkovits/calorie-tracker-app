import os
import pandas as pd


empty_dfs = {
    "new_recipe_ingredients": pd.DataFrame(columns=["ingredient", "quantity", "serving"]),
    "new_recipe_instructions": pd.DataFrame(columns=["instruction"]),
    "new_recipe_tags": pd.DataFrame(columns=["tag"]),
}

def load_from_local_cache(file_name: str) -> pd.DataFrame:
    file_path = file_name + ".csv"
    if not os.path.exists(file_path):
        return empty_dfs[file_name]
    return pd.read_csv(file_path)
