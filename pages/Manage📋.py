import streamlit as st
import pandas as pd
import numpy as np
from datetime import datetime
from google_sheets import GoogleSheetsInterface
from local_cache import LocalCacheInterface

gsheets = GoogleSheetsInterface()
local = LocalCacheInterface()

df_food_data = gsheets.load_google_sheet_data(sheet_name="food_data")
df_available_tags = gsheets.load_google_sheet_data(sheet_name="available_tags")

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


st.set_page_config(page_title="Manage Data", page_icon="📋")

st.markdown("# View & Edit Data 📋")
st.sidebar.header("Manage")
st.write(
    """
    Manage the data in the Google Sheet.
    """
)

st.divider()

st.write("### Food Items")

st.write("Add or remove food items from the food/nutrition database stored in Google Sheet.")

mode = st.pills("Mode", ["Add", "Remove"], help="Select the mode to view or edit food items", default="Add", label_visibility="hidden", key="mode_food_items")

if mode == "Add":
    st.write("##### Food Item Details")
    col1, col2 = st.columns(2)
    with col1:
        name = st.text_input("Name", value="")
    with col2:
        type = st.selectbox("Type", options=df_food_data["Type"].unique())

    st.write("##### Nutritional Value per 100g")
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        calories = st.number_input("Calories (kcal)", value=0)
    with col2:
        fat = st.number_input("Fat (g)", value=0.)
    with col3:
        carbs = st.number_input("Carbs (g)", value=0.)
    with col4:
        protein = st.number_input("Protein (g)", value=0.)


    st.write("##### Serving Size")
    col1, col2 = st.columns(2)
    with col1:
        serving_name = st.text_input("Serving Name", value="portion(s)")
    with col2:
        serving_size = st.number_input("Single Serving Size (g)", value=100)

    if st.button("Add Food Item"):
        names = df_food_data["Name"].to_list()
        if name in names:
            st.error(f"A food item with the name '{name}' already exists! Please use a different name.")
            st.stop()
        new_row = {
            "Name": name,
            "Fat (g)": fat,
            "Carbs (g)": carbs,
            "Protein (g)": protein,
            "Calories (kcal)": calories,
            "Serving Name": serving_name,
            "Single Serving (g)": serving_size,
            "Type": type,
        }
        df_food_data = pd.concat([df_food_data, pd.DataFrame([new_row])], ignore_index=True)
        gsheets.update_google_sheet(sheet_name="food_data", updated_data=df_food_data)
        st.success("Food item added successfully!")
        st.rerun()

elif mode == "Remove":
    food_items = df_food_data["Name"].unique()
    food_item = st.selectbox("Select a food item", food_items)
    st.write(df_food_data[df_food_data["Name"] == food_item])

    if st.button("Remove Food Item"):
        df_food_data = df_food_data[df_food_data["Name"] != food_item]
        gsheets.update_google_sheet(sheet_name="food_data", updated_data=df_food_data)
        st.success("Food item removed successfully!")
        st.rerun()

st.divider()
st.write("### Recipe Tags")
st.write("Add or remove tags from the recipe database stored in Google Sheet.")
mode = st.pills("Mode", ["Add", "Remove"], help="Select the mode to view or edit recipe tags", default="Add", label_visibility="hidden", key="mode_recipe_tags")

if mode == "Add":
    tag = st.text_input("Tag", value="")
    if st.button("Add Tag"):
        tags = df_available_tags["tag"].unique()
        if tag in tags:
            st.error(f"A tag with the name '{tag}' already exists! Please use a different name.")
            st.stop()

        new_row = {
            "tag": tag
        }
        df_available_tags = pd.concat([df_available_tags, pd.DataFrame([new_row])], ignore_index=True)
        gsheets.update_google_sheet(sheet_name="available_tags", updated_data=df_available_tags)
        st.success("Tag added successfully!")
        st.rerun()
elif mode == "Remove":
    tags = df_available_tags["tag"].unique()
    tag = st.selectbox("Select a tag", tags)

    if st.button("Remove Tag"):
        df_available_tags = df_available_tags[df_available_tags["tag"] != tag]
        gsheets.update_google_sheet(sheet_name="available_tags", updated_data=df_available_tags)
        st.success("Tag removed successfully!")
        st.rerun()

st.divider()
st.write("### Recipes")
mode = st.pills("Mode", ["Add", "Remove"], help="Select the mode to view or edit recipes", default="Add", label_visibility="hidden", key="mode_recipes")

if mode == "Add":
    with st.expander("Recipe Info", expanded=True):
        # st.write("### Recipe Info")
        recipe_name = st.text_input("Recipe Name", placeholder="Recipe Name", label_visibility="hidden")
        tags = st.multiselect("Tags", df_available_tags["tag"].unique(), placeholder="Tags", label_visibility="hidden")
        description = st.text_area("Description", placeholder="Description", label_visibility="hidden")

        st.divider()

    with st.expander("Ingredients", expanded=False):
    # st.write("### Ingredients")
        servings = st.slider("Recipe serves", min_value=1, max_value=10, value=2)
        st.dataframe(df_new_recipe_ingredients)

        if st.button("Clear Ingredients"):
            local.clear_local_cache("new_recipe_ingredients")
            st.rerun()

        col1, col2, col3 = st.columns(3)
        with col1:
            ingredient = st.selectbox("Ingredient", df_food_data["Name"].unique())
            # b1 = st.button("Add Ingredient")
        with col2:
            quantity = st.number_input("Quantity", min_value=0.0, step=0.1, value=1.0)
            # b2 = st.button("Clear Ingredients")
        with col3:
            serving = st.selectbox("Serving", [df_food_data.loc[df_food_data["Name"] == ingredient, "Serving Name"].values[0], "g"])


        if st.button("Add Ingredient"):
            st.write("Ingredient added:", ingredient, quantity, serving)
            df_new_row = pd.DataFrame(
                [[ingredient, quantity, serving]],
                columns=["ingredient", "quantity", "serving"]
            )
            if df_new_recipe_ingredients.empty:
                df_new_recipe_ingredients = df_new_row
            else:
                df_new_recipe_ingredients = pd.concat([df_new_recipe_ingredients, df_new_row])

            local.update_local_cache("new_recipe_ingredients", df_new_recipe_ingredients)
            st.rerun()


    with st.expander("Instructions", expanded=False):
    # st.write("### Instructions")
        df_new_recipe_instructions = st.data_editor(df_new_recipe_instructions, num_rows="dynamic")
        instruction = st.text_input("Instruction")
        if st.button("Add Instruction"):
            df_new_row = pd.DataFrame(
                [[instruction]],
                columns=["instruction"]
            )
            if df_new_recipe_instructions.empty:
                df_new_recipe_instructions = df_new_row
            else:
                df_new_recipe_instructions = pd.concat([df_new_recipe_instructions, df_new_row])
            local.update_local_cache("new_recipe_instructions", df_new_recipe_instructions)
            st.rerun()


    if st.button("Save Recipe"):
        if recipe_name in df_info["name"].values:
            st.error(f"A recipe with the name '{recipe_name}' already exists! Please use a different name.")
            st.stop()

        df_new_recipe_info = pd.DataFrame({"name": [recipe_name], "description": [description]})
        df_new_recipe_tags = pd.DataFrame({"name": [recipe_name]*len(tags), "tag": tags})
        df_new_recipe_ingredients["name"] = recipe_name
        df_new_recipe_ingredients["quantity"] = df_new_recipe_ingredients["quantity"]/servings
        df_new_recipe_instructions["name"] = recipe_name

        df_new_recipe_ingredients = df_new_recipe_ingredients[["name", "ingredient", "quantity", "serving"]]
        df_new_recipe_instructions = df_new_recipe_instructions[["name", "instruction"]]

        df_info = pd.concat([df_info, df_new_recipe_info])
        df_tags = pd.concat([df_tags, df_new_recipe_tags])
        df_ingredients = pd.concat([df_ingredients, df_new_recipe_ingredients])
        df_instructions = pd.concat([df_instructions, df_new_recipe_instructions])

        gsheets.update_google_sheet("recipe_info", df_info)
        gsheets.update_google_sheet("recipe_tags", df_tags)
        gsheets.update_google_sheet("recipe_ingredients", df_ingredients)
        gsheets.update_google_sheet("recipe_instructions", df_instructions)
        st.success("Recipe saved successfully!")


elif mode == "Remove":
    recipe_names = df_info["name"].unique()
    recipe_name = st.selectbox("Select a recipe", recipe_names)

    if st.button("Remove Recipe"):
        df_info = df_info[df_info["name"] != recipe_name]
        df_tags = df_tags[df_tags["name"] != recipe_name]
        df_ingredients = df_ingredients[df_ingredients["name"] != recipe_name]
        df_instructions = df_instructions[df_instructions["name"] != recipe_name]

        gsheets.update_google_sheet("recipe_info", df_info)
        gsheets.update_google_sheet("recipe_tags", df_tags)
        gsheets.update_google_sheet("recipe_ingredients", df_ingredients)
        gsheets.update_google_sheet("recipe_instructions", df_instructions)
        st.success("Recipe removed successfully!")
        st.rerun()


st.divider()
st.write("### Edit Raw Data")
sheet_name = st.selectbox("Select a sheet", [
    "food_data",
    "food_log_bela",
    "food_log_marleen",
    "target_bela",
    "target_marleen",
    "weight_log_bela",
    "weight_log_marleen"
])

data = gsheets.load_google_sheet_data(sheet_name=sheet_name)
df = st.data_editor(data, num_rows="dynamic")

if st.button("Save Changes"):
    gsheets.update_google_sheet(sheet_name=sheet_name, updated_data=df)
    st.success("Google Sheet updated successfully!")
