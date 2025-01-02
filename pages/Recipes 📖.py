import streamlit as st
import pandas as pd
import numpy as np
from datetime import datetime
from google_sheets import GoogleSheetsInterface
from local_cache import LocalCacheInterface
import os

gsheets = GoogleSheetsInterface()
local = LocalCacheInterface()

df_info = gsheets.load_google_sheet_data(sheet_name="recipe_info")
df_tags = gsheets.load_google_sheet_data(sheet_name="recipe_tags")
df_ingredients = gsheets.load_google_sheet_data(sheet_name="recipe_ingredients")
df_instructions = gsheets.load_google_sheet_data(sheet_name="recipe_instructions")
df_food_data = gsheets.load_google_sheet_data(sheet_name="food_data")
df_available_tags = gsheets.load_google_sheet_data(sheet_name="available_tags")

df_new_recipe_info = local.load_from_local_cache("new_recipe_info")
df_new_recipe_tags = local.load_from_local_cache("new_recipe_tags")
df_new_recipe_ingredients = local.load_from_local_cache("new_recipe_ingredients")
df_new_recipe_instructions = local.load_from_local_cache("new_recipe_instructions")


st.set_page_config(page_title="Recipes", page_icon="📖")

st.markdown("# Recipes 📖")
st.sidebar.header("Recipes")
st.write(
    """
    View and edit recipes.
    """
)


tags = st.multiselect("Tags", list(df_available_tags["tag"].unique()), help="Filter recipes by tags", placeholder="Select tags", label_visibility="hidden")
df_names = df_tags.groupby("name").filter(lambda x: set(tags).issubset(set(x["tag"])))

names = df_names["name"].unique()

for recipe_name in names:
    d1 = df_tags[df_tags["name"] == recipe_name]
    d2 = df_info[df_info["name"] == recipe_name]
    d3 = df_ingredients[df_ingredients["name"] == recipe_name]
    d4 = df_instructions[df_instructions["name"] == recipe_name]


    st.write(f"#### {recipe_name}")
    recipe_tags = d1["tag"].to_list()
    tag_markdown = [
        "<style>\n",
        "    .tag {\n",
        "        display: inline-block;\n",
        "        border-radius: 5px;\n",
        "        color: white;\n",
        "        padding: 0.1em 0.5em;\n",
        "        background: rgb(255, 75, 75);\n", # red
        # "        background: rgb(75, 196, 255);\n", # blue
        # "        border: 1px solid rgb(255, 75, 75);\n", #red
        "        margin: .1em .1em\n",
        "    }\n",
        "</style>\n",
        "\n",
    ]
    for tag in recipe_tags:
        tag_markdown.append(f"<span class='tag'>{tag}</span>\n")

    st.write("".join(tag_markdown), unsafe_allow_html=True)
    # st.markdown(f"![{recipe_name}](https://plus.unsplash.com/premium_photo-1673108852149-85f46a4dee4b?q=80&w=2564&auto=format&fit=crop&ixlib=rb-4.0.3&ixid=M3wxMjA3fDB8MHxwaG90by1wYWdlfHx8fGVufDB8fHx8fA%3D%3D)")
    st.write(d2['description'].values[0])

    with st.expander("Full Recipe"):

        st.header("Ingredients")
        n_servings = st.slider("Number of servings", min_value=1, max_value=10, value=2, key=f"serving_{recipe_name}")

        def calc_weight(row):
            if row["serving"] == "g":
                return row["quantity"]
            else:
                return row["quantity"] * row["Single Serving (g)"]

        df3 = d3.merge(df_food_data, left_on="ingredient", right_on="Name", how="left")
        df3["quantity"] = df3["quantity"]*n_servings
        df3["weight"] = df3.apply(calc_weight, axis=1)
        df3["calories"] = df3["Calories (kcal)"] * df3["weight"] / 100

        df3 = df3[["ingredient", "quantity", "serving", "weight", "calories"]]
        df3 = df3.rename(columns={"ingredient": "Ingredient", "quantity": "Quantity", "serving": "Serving", "weight": "Weight (g)", "calories": "Calories (kcal)"})
        st.write(df3)

        st.write(f"""
            * Total Calories: {df3["Calories (kcal)"].sum()} kcal
            * Calorise per serving: {df3["Calories (kcal)"].sum() / n_servings} kcal
        """)

        st.header("Instructions")
        instructions = d4["instruction"].to_list()
        st.write("".join(f"* {instruction} \n" for instruction in instructions))
