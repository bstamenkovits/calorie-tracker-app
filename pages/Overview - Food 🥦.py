import streamlit as st
import pandas as pd
from google_sheets import GoogleSheetsInterface
from datetime import datetime

gsheets = GoogleSheetsInterface()


st.set_page_config(
    page_title="Food Overview",
    page_icon="🥦",
)

st.write("# Food Overview 🥦")
st.write("View and Log Food and Calorie Intake")

who = st.selectbox("Who", options=["Bela", "Marleen"])
date = st.date_input("Date", value=pd.to_datetime("today"))

df_food_data = gsheets.load_google_sheet_data(sheet_name="food_data")
df_food_log = gsheets.load_google_sheet_data(sheet_name=f"food_log_{who.lower()}")
df_weight_log = gsheets.load_google_sheet_data(sheet_name=f"weight_log_{who.lower()}")
df_exercise_log = gsheets.load_google_sheet_data(sheet_name=f"exercise_log_{who.lower()}")

date = date.strftime("%Y-%m-%d")

def calc_weight(row):
    if row["serving"]=="g":
        return row["quantity"]
    else:
        return row["quantity"] * row["Single Serving (g)"]

def calc_total_calories(row):
    return round(row["weight"] * row["Calories (kcal)"]/100, 0)



df_day = df_food_log[(df_food_log["date"]==date)]
df_day = df_day.merge(df_food_data, left_on="name", right_on="Name", how="left")
df_day["weight"] = df_day.apply(calc_weight, axis=1)
df_day["total_calories"] = df_day.apply(calc_total_calories, axis=1)
df_day = df_day.rename(columns={
    "name": "Food",
    "quantity": "Quantity",
    "serving": "Serving",
    "total_calories": "Calories"
})

calories_by_meal = df_day.groupby("meal")["Calories"].sum()


# Create a stacked bar chart
calories_by_meal = calories_by_meal.reset_index()
calories_by_meal = calories_by_meal.transpose()

# assign meal as column header
calories_by_meal.columns = calories_by_meal.iloc[0]
calories_by_meal = calories_by_meal[1:]
calories_by_meal.reset_index(drop=True, inplace=True)

current_weight = float(df_weight_log["weight"].values[-1])

def calculate_energy_burned(weight, height, birthday, exercise_level):
    exercise_map = {
        0: 1.2,
        1: 1.375,
        2: 1.4625,
        3: 1.55,
        4: 1.725,
        5: 1.9
    }
    age = (datetime.today() - birthday).days / 365
    BMR = 10 * weight + 6.25 * height - 5 * age
    return BMR * exercise_map[exercise_level]

df_info = gsheets.load_google_sheet_data(sheet_name=f"info_{who.lower()}")

height = df_info["height"].values[0]
birthday = pd.to_datetime(df_info["birthday"].values[0])

st.write("### Today's Energy Overview")
# exercise_level = st.selectbox("Exercise Level", options = [0, 1, 2, 3, 4, 5], default=2)
exercise_level = st.slider("Exercise Level", min_value=0, max_value=5, value=2, step=1)
capacity = calculate_energy_burned(current_weight, height, birthday, exercise_level)

df_target = gsheets.load_google_sheet_data(sheet_name=f"target_{who.lower()}")
target = df_target["target"].values[0]

capacity = capacity - target

consumed = calories_by_meal.sum(axis=1)
remaining = capacity - consumed
calories_by_meal['_Remaining'] = remaining
for meal in ["Breakfast", "Lunch", "Dinner", "Snack"]:
    if meal not in calories_by_meal.columns:
        calories_by_meal[meal] = 0
calories_by_meal = calories_by_meal[["Breakfast", "Lunch", "Dinner", "Snack", "_Remaining"]]
calories_by_meal = calories_by_meal.rename(columns={"Breakfast": "1. 🍌 Breakfast", "Lunch": "2. 🥗 Lunch", "Dinner": "3. 🥗 Dinner", "Snack": "4. 🍙 Snack", "_Remaining": "🔥 Remaining"})


if remaining.values[0] > 0:
    st.write(f"#### Great Job!", unsafe_allow_html=True)
    st.markdown(f"<span style='font-weight:bold'>Consumed: {round(consumed.to_list()[0])} kcal </span>", unsafe_allow_html=True)
    st.markdown(f"<span style='color:green; font-weight:bold'>Remaining: {round(float(remaining.values[0]))} kcal </span>", unsafe_allow_html=True)
    colors = ("#d66154", "#dbd5ba", "#48ab8a", "#8db6c3", "#898989")
    colors = ("#bababa", "#9f9f9f", "#616161", "#4b4b4b", "#209253")
else:
    st.write(f"#### Oh No!", unsafe_allow_html=True)
    st.markdown(f"<span style='font-weight:bold'>Consumed: {round(consumed.to_list()[0])} kcal </span>", unsafe_allow_html=True)
    st.markdown(f"<span style='color:red'>You have exceeded your daily calorie intake by {-remaining.values[0]} kcal</span>", unsafe_allow_html=True)
    colors = ("#d66154", "#dbd5ba", "#48ab8a", "#8db6c3", "#dd2e44")
    colors = ("#bababa", "#9f9f9f", "#616161", "#4b4b4b", "#ab3f3f")
st.bar_chart(calories_by_meal, horizontal=True, color=colors)

st.divider()

df_breakfast = df_day[df_day["meal"]=="Breakfast"]
df_lunch = df_day[df_day["meal"]=="Lunch"]
df_dinner = df_day[df_day["meal"]=="Dinner"]
df_snack = df_day[df_day["meal"]=="Snack"]


st.write(f"### 🍌 Breakfast")
st.dataframe(df_breakfast[["Food", "Quantity", "Serving", "Calories"]])
st.write(f"###### Total Calories: {df_breakfast['Calories'].sum()} kcal")


with st.expander("Add Breakfast Food Log"):
    meal = "Breakfast"
    # st.write("###### What ❓")
    type = st.selectbox("Type of Food", options = df_food_data["Type"].unique(), key=f"type_{meal}")
    name = st.selectbox("Food Name", options=df_food_data[df_food_data["Type"]==type].sort_values(by="Name")["Name"], key=f"name_{meal}")

    # st.write("###### Amount ⚖️")
    serving_options = df_food_data[df_food_data["Name"]==name]["Serving Name"].to_list()
    serving_options.append("g")
    serving = st.selectbox("Type of serving", options=serving_options, key=f"serving_{meal}")

    if serving == "g":
        quantity = st.number_input("Quantity (g)", min_value=0, step=1, key=f"quantity_{meal}")
        weight = quantity
    else:
        quantity = st.selectbox("Servings", options=[i for i in range(1, 11)], key=f"quantity_{meal}")
        weight = (quantity * df_food_data[df_food_data["Name"]==name]["Single Serving (g)"]).values[0]

    kcal_per_100g = df_food_data[df_food_data["Name"]==name]["Calories (kcal)"].values[0]
    kcal = (kcal_per_100g * weight) / 100
    st.write(f"###### For {meal}, {quantity} {serving} of {name} =  {kcal} kcal")

    if st.button("Add Food", key=f"button_{meal}"):
        df_food_log = gsheets.load_google_sheet_data(sheet_name=f"food_log_{who.lower()}")
        new_row = {
            "date": date,
            "meal": meal,
            "name": name,
            "quantity": quantity,
            "serving": serving,
        }
        df_food_log = pd.concat([df_food_log, pd.DataFrame([new_row])], ignore_index=True)

        st.write("updated data:")
        st.dataframe(df_food_log.tail(1))

        gsheets.update_google_sheet(
            sheet_name=f"food_log_{who.lower()}",
            updated_data=df_food_log
        )
        st.success("Food log added successfully!")

st.write(f"### 🥗 Lunch")
st.dataframe(df_lunch[["Food", "Quantity", "Serving", "Calories"]])
st.write(f"###### Total Calories: {df_lunch['Calories'].sum()} kcal")
with st.expander("Add Lunch Food Log"):
    meal = "Lunch"
    # st.write("###### What ❓")
    type = st.selectbox("Type of Food", options = df_food_data["Type"].unique(), key=f"type_{meal}")
    name = st.selectbox("Food Name", options=df_food_data[df_food_data["Type"]==type].sort_values(by="Name")["Name"], key=f"name_{meal}")

    # st.write("###### Amount ⚖️")
    serving_options = df_food_data[df_food_data["Name"]==name]["Serving Name"].to_list()
    serving_options.append("g")
    serving = st.selectbox("Type of serving", options=serving_options, key=f"serving_{meal}")

    if serving == "g":
        quantity = st.number_input("Quantity (g)", min_value=0, step=1, key=f"quantity_{meal}")
        weight = quantity
    else:
        quantity = st.selectbox("Servings", options=[i for i in range(1, 11)], key=f"quantity_{meal}")
        weight = (quantity * df_food_data[df_food_data["Name"]==name]["Single Serving (g)"]).values[0]

    kcal_per_100g = df_food_data[df_food_data["Name"]==name]["Calories (kcal)"].values[0]
    kcal = (kcal_per_100g * weight) / 100
    st.write(f"###### For {meal}, {quantity} {serving} of {name} =  {kcal} kcal")

    if st.button("Add Food", key=f"button_{meal}"):
        df_food_log = gsheets.load_google_sheet_data(sheet_name=f"food_log_{who.lower()}")
        new_row = {
            "date": date,
            "meal": meal,
            "name": name,
            "quantity": quantity,
            "serving": serving,
        }
        df_food_log = pd.concat([df_food_log, pd.DataFrame([new_row])], ignore_index=True)

        st.write("updated data:")
        st.dataframe(df_food_log.tail(1))

        gsheets.update_google_sheet(
            sheet_name=f"food_log_{who.lower()}",
            updated_data=df_food_log
        )
        st.success("Food log added successfully!")


st.write(f"### 🍗 Dinner")
st.dataframe(df_dinner[["Food", "Quantity", "Serving", "Calories"]])
st.write(f"###### Total Calories: {df_dinner['Calories'].sum()} kcal")
with st.expander("Add Dinner Food Log"):
    meal = "Dinner"
    # st.write("###### What ❓")
    type = st.selectbox("Type of Food", options = df_food_data["Type"].unique(), key=f"type_{meal}")
    name = st.selectbox("Food Name", options=df_food_data[df_food_data["Type"]==type].sort_values(by="Name")["Name"], key=f"name_{meal}")

    # st.write("###### Amount ⚖️")
    serving_options = df_food_data[df_food_data["Name"]==name]["Serving Name"].to_list()
    serving_options.append("g")
    serving = st.selectbox("Type of serving", options=serving_options, key=f"serving_{meal}")

    if serving == "g":
        quantity = st.number_input("Quantity (g)", min_value=0, step=1, key=f"quantity_{meal}")
        weight = quantity
    else:
        quantity = st.selectbox("Servings", options=[i for i in range(1, 11)], key=f"quantity_{meal}")
        weight = (quantity * df_food_data[df_food_data["Name"]==name]["Single Serving (g)"]).values[0]

    kcal_per_100g = df_food_data[df_food_data["Name"]==name]["Calories (kcal)"].values[0]
    kcal = (kcal_per_100g * weight) / 100
    st.write(f"###### For {meal}, {quantity} {serving} of {name} =  {kcal} kcal")

    if st.button("Add Food", key=f"button_{meal}"):
        df_food_log = gsheets.load_google_sheet_data(sheet_name=f"food_log_{who.lower()}")
        new_row = {
            "date": date,
            "meal": meal,
            "name": name,
            "quantity": quantity,
            "serving": serving,
        }
        df_food_log = pd.concat([df_food_log, pd.DataFrame([new_row])], ignore_index=True)

        st.write("updated data:")
        st.dataframe(df_food_log.tail(1))

        gsheets.update_google_sheet(
            sheet_name=f"food_log_{who.lower()}",
            updated_data=df_food_log
        )
        st.success("Food log added successfully!")


st.write(f"### 🍙 Snack")
st.dataframe(df_snack[["Food", "Quantity", "Serving", "Calories"]])
st.write(f"###### Total Calories: {df_snack['Calories'].sum()} kcal")
with st.expander("Add Snack Food Log"):
    meal = "Snack"
    # st.write("###### What ❓")
    type = st.selectbox("Type of Food", options = df_food_data["Type"].unique(), key=f"type_{meal}")
    name = st.selectbox("Food Name", options=df_food_data[df_food_data["Type"]==type].sort_values(by="Name")["Name"], key=f"name_{meal}")

    # st.write("###### Amount ⚖️")
    serving_options = df_food_data[df_food_data["Name"]==name]["Serving Name"].to_list()
    serving_options.append("g")
    serving = st.selectbox("Type of serving", options=serving_options, key=f"serving_{meal}")

    if serving == "g":
        quantity = st.number_input("Quantity (g)", min_value=0, step=1, key=f"quantity_{meal}")
        weight = quantity
    else:
        quantity = st.selectbox("Servings", options=[i for i in range(1, 11)], key=f"quantity_{meal}")
        weight = (quantity * df_food_data[df_food_data["Name"]==name]["Single Serving (g)"]).values[0]

    kcal_per_100g = df_food_data[df_food_data["Name"]==name]["Calories (kcal)"].values[0]
    kcal = (kcal_per_100g * weight) / 100
    st.write(f"###### For {meal}, {quantity} {serving} of {name} =  {kcal} kcal")

    if st.button("Add Food", key=f"button_{meal}"):
        df_food_log = gsheets.load_google_sheet_data(sheet_name=f"food_log_{who.lower()}")
        new_row = {
            "date": date,
            "meal": meal,
            "name": name,
            "quantity": quantity,
            "serving": serving,
        }
        df_food_log = pd.concat([df_food_log, pd.DataFrame([new_row])], ignore_index=True)

        st.write("updated data:")
        st.dataframe(df_food_log.tail(1))

        gsheets.update_google_sheet(
            sheet_name=f"food_log_{who.lower()}",
            updated_data=df_food_log
        )
        st.success("Food log added successfully!")

# st.sidebar.success("Go to section...")
