import streamlit as st
import pandas as pd
import numpy as np
from datetime import datetime
from google_sheets import GoogleSheetsInterface
from local_cache import load_from_local_cache
import os

gsheets = GoogleSheetsInterface()

df_ingredients = gsheets.load_google_sheet_data(sheet_name="recipe_ingredients")
df_instructions = gsheets.load_google_sheet_data(sheet_name="recipe_instructions")
df_tags = gsheets.load_google_sheet_data(sheet_name="recipe_tags")
df_food_data = gsheets.load_google_sheet_data(sheet_name="food_data")

df_new_recipe_ingredients = load_from_local_cache("new_recipe_ingredients")
df_new_recipe_instructions = load_from_local_cache("new_recipe_instructions")
df_new_recipe_tags = load_from_local_cache("new_recipe_tags")

st.set_page_config(page_title="Recipes", page_icon="🔪")

st.markdown("# Recipes 🔪")
st.sidebar.header("Recipes")
st.write(
    """
    View and edit recipes.
    """
)

def update_local_cache(file_name: str, df: pd.DataFrame):
    file_path = file_name + ".csv"
    df.to_csv(file_path, index=False)
    st.rerun()






mode = st.pills("Mode", ["View", "Add"], help="Select the mode to view or edit recipes", default="Add")

# if mode == "Edit":

if mode == "View":
    tags = st.multiselect("Tags", list(df_tags["tag"].unique()), help="Filter recipes by tags")
    df_names = df_tags.groupby("name").filter(lambda x: set(tags).issubset(set(x["tag"])))

    names = df_names["name"].unique()


    for recipe_name in names:
        d1 = df_ingredients[df_ingredients["name"] == recipe_name]
        d2 = df_instructions[df_instructions["name"] == recipe_name]
        d3 = df_tags[df_tags["name"] == recipe_name]

        st.write(f"#### {recipe_name}")
        recipe_tags = d3["tag"].to_list()
        tag_markdown = [
            "<style>\n",
            "    .tag {\n",
            "        display: inline-block;\n",
            "        border-radius: 4px;\n",
            "        color: white;\n",
            "        padding: 0.1em 0.5em;\n",
            # "        background: rgb(255, 75, 75);\n", # red
            "        background: rgb(75, 196, 255);\n", # blue
            "        margin: .1em .1em\n",
            "    }\n",
            "</style>\n",
            "\n",
        ]
        for tag in recipe_tags:
            tag_markdown.append(f"<span class='tag'>{tag}</span>\n")

        st.write("".join(tag_markdown), unsafe_allow_html=True)
        # st.markdown(f"![{recipe_name}](https://plus.unsplash.com/premium_photo-1673108852149-85f46a4dee4b?q=80&w=2564&auto=format&fit=crop&ixlib=rb-4.0.3&ixid=M3wxMjA3fDB8MHxwaG90by1wYWdlfHx8fGVufDB8fHx8fA%3D%3D)")
        with st.expander("Full Recipe"):

            st.header("Ingredients")
            n_servings = st.slider("Number of servings", min_value=1, max_value=10, value=2, key=f"serving_{recipe_name}")

            def calc_weight(row):
                if row["serving"] == "g":
                    return row["quantity"]
                else:
                    return row["quantity"] * row["Single Serving (g)"]

            df1 = d1.merge(df_food_data, left_on="ingredient", right_on="Name", how="left")
            df1["quantity"] = df1["quantity"]*n_servings
            df1["weight"] = df1.apply(calc_weight, axis=1)
            df1["calories"] = df1["Calories (kcal)"] * df1["weight"] / 100

            df1 = df1[["ingredient", "quantity", "serving", "weight", "calories"]]
            df1 = df1.rename(columns={"ingredient": "Ingredient", "quantity": "Quantity", "serving": "Serving", "weight": "Weight (g)", "calories": "Calories (kcal)"})
            st.write(df1)

            st.write(f"""
                * Total Calories: {df1["Calories (kcal)"].sum()} kcal
                * Calorise per serving: {df1["Calories (kcal)"].sum() / n_servings} kcal
            """)

            st.header("Instructions")
            instructions = d2["instructions"].to_list()
            st.write("".join(f"* {instruction} \n" for instruction in instructions))

elif mode == "Add":
    st.write("### Recipe Info")
    recipe_name = st.text_input("Recipe Name", placeholder="Recipe Name", label_visibility="hidden")
    description = st.text_area("Description", placeholder="Description", label_visibility="hidden")
    tags = st.multiselect("Tags", df_tags["tag"].unique(), placeholder="Tags", label_visibility="hidden")

    st.divider()

    st.write("### Ingredients")
    df_new_recipe_ingredients = st.data_editor(df_new_recipe_ingredients, num_rows="dynamic")





    col1, col2, col3 = st.columns(3)
    with col1:
        ingredient = st.selectbox("Ingredient", df_food_data["Name"].unique())
        # b1 = st.button("Add Ingredient")
    with col2:
        quantity = st.number_input("Quantity", min_value=0.0, step=0.1, value=1.0)
        # b2 = st.button("Clear Ingredients")
    with col3:
        serving = st.selectbox("Serving", [df_food_data.loc[df_food_data["Name"] == ingredient, "Serving Name"].values[0], "g"])

    # left, right = st.columns(2)

    # with left:
    #     b1 = st.button("Add Ingredient")
    # with right:
    #     b2 = st.button("Clear Ingredients")

    if st.button("Clear Ingredients"):
        print()
    if st.button("Add Ingredient"):
        print()
    #     st.write("Ingredient added:", ingredient, quantity, serving)
    #     df_new_row = pd.DataFrame(
    #         [[ingredient, quantity, serving]],
    #         columns=["ingredient", "quantity", "serving"]
    #     )
    #     if df_new_recipe_ingredients.empty:
    #         df_new_recipe_ingredients = df_new_row
    #     else:
    #         df_new_recipe_ingredients = pd.concat([df_new_recipe_ingredients, df_new_row])

    #     update_local_cache("new_recipe_ingredients", df_new_recipe_ingredients)

    st.divider()
    st.write("### Instructions")
    df_new_recipe_instructions = st.data_editor(df_new_recipe_instructions, num_rows="dynamic")
    instruction = st.text_input("Instruction")
    if st.button("Add Instruction"):
        print()
    #     df_new_row = pd.DataFrame(
    #         [[instruction]],
    #         columns=["instruction"]
    #     )
    #     if df_new_recipe_instructions.empty:
    #         df_new_recipe_instructions = df_new_row
    #     else:
    #         df_new_recipe_instructions = pd.concat([df_new_recipe_instructions, df_new_row])
    #     update_local_cache("new_recipe_instructions", df_new_recipe_instructions)


    # st.write("### Tags")
    # df_new_recipe_tags = st.data_editor(df_new_recipe_tags, num_rows="dynamic")


    # st.write("### Save Recipe")
    # if st.button("Save Recipe"):
    #     st.success("Recipe saved successfully!")

# elif mode == "Edit":
#     if st.button("Add Recipe"):
#         print()

#     st.divider()
#     name = st.selectbox("Select a recipe", df_instructions["name"].unique())

#     st.header("Edit Recipe")
#     recipe_name = st.text_input("Recipe Name")
#     st.write("### Ingredients")
#     df_new_recipe_ingredients = st.data_editor(df_new_recipe_ingredients, num_rows="dynamic")

#     ingredient = st.selectbox("Ingredient", df_food_data["Name"].unique())
#     quantity = st.number_input("Quantity", min_value=0.0, step=0.1, value=1.0)
#     serving = st.selectbox("Serving", [df_food_data.loc[df_food_data["Name"] == ingredient, "Serving Name"].values[0], "g"])

#     if st.button("Add Ingredient"):
#         st.write("Ingredient added:", ingredient, quantity, serving)
#         df_new_row = pd.DataFrame(
#             [[ingredient, quantity, serving]],
#             columns=["ingredient", "quantity", "serving"]
#         )
#         if df_new_recipe_ingredients.empty:
#             df_new_recipe_ingredients = df_new_row
#         else:
#             df_new_recipe_ingredients = pd.concat([df_new_recipe_ingredients, df_new_row])

#         update_local_cache("new_recipe_ingredients", df_new_recipe_ingredients)

#     st.write("### Instructions")
#     df_new_recipe_instructions = st.data_editor(df_new_recipe_instructions, num_rows="dynamic")
#     instruction = st.text_input("Instruction")
#     if st.button("Add Instruction"):
#         df_new_row = pd.DataFrame(
#             [[instruction]],
#             columns=["instruction"]
#         )
#         if df_new_recipe_instructions.empty:
#             df_new_recipe_instructions = df_new_row
#         else:
#             df_new_recipe_instructions = pd.concat([df_new_recipe_instructions, df_new_row])
#         update_local_cache("new_recipe_instructions", df_new_recipe_instructions)


#     st.write("### Tags")
#     df_new_recipe_tags = st.data_editor(df_new_recipe_tags, num_rows="dynamic")
#     tag = st.text_input("Tag")

#     st.write("### Save Recipe")
#     if st.button("Save Recipe"):
#         st.success("Recipe saved successfully!")

# elif mode == "Edit":
#     st.selectbox("Select a recipe", df_instructions["name"].unique())
# recipe_name:str = st.selectbox("Select a recipe", df_instructions["name"].unique())
