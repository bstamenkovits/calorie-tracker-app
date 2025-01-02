import streamlit as st
import pandas as pd
from google_sheets import GoogleSheetsInterface
from datetime import datetime
import time
from gspread.exceptions import APIError

gsheets = GoogleSheetsInterface()

st.set_page_config(
    page_title="Food Overview",
    page_icon="🥦",
)

st.write("# Food Overview 🥦")
st.write("View and Log Food and Calorie Intake")

who = st.pills("Who", options=["Bela", "Marleen"], default="Bela", selection_mode="single")
date = st.date_input("Date", value=pd.to_datetime("today"))
date = date.strftime("%Y-%m-%d")

try:
    df_food_data = gsheets.load_google_sheet_data(sheet_name="food_data")
    df_food_log = gsheets.load_google_sheet_data(sheet_name=f"food_log_{who.lower()}")
    df_weight_log = gsheets.load_google_sheet_data(sheet_name=f"weight_log_{who.lower()}")
    df_info = gsheets.load_google_sheet_data(sheet_name=f"info_{who.lower()}")
    df_target = gsheets.load_google_sheet_data(sheet_name=f"target_{who.lower()}")
except APIError as e:
    st.warning("Exceeded Google Sheets API quota. Please wait...")
    time.sleep(10)


def calc_weight(row):
    if row["serving"]=="g":
        return row["quantity"]
    else:
        return row["quantity"] * row["Single Serving (g)"]

def calc_total_calories(row):
    return round(row["weight"] * row["Calories (kcal)"]/100, 0)

# filter for a single day
df_day = df_food_log[(df_food_log["date"]==date)]

# Add relevant food data
df_day = df_day.merge(df_food_data, left_on="name", right_on="Name", how="left")
df_day["weight"] = df_day.apply(calc_weight, axis=1)
df_day["total_calories"] = df_day.apply(calc_total_calories, axis=1)

# rename columns to be displayed
df_day = df_day.rename(columns={
    "name": "Food",
    "quantity": "Quantity",
    "serving": "Serving",
    "total_calories": "Calories"
})

# summary of calories by meal
calories_by_meal = df_day.groupby("meal")["Calories"].sum()

# Create a stacked bar chart
calories_by_meal = calories_by_meal.reset_index()
calories_by_meal = calories_by_meal.transpose()

# assign meal as column header
calories_by_meal.columns = calories_by_meal.iloc[0]
calories_by_meal = calories_by_meal[1:]
calories_by_meal.reset_index(drop=True, inplace=True)

def calculate_energy_burned(weight, height, birthday, exercise_level, sex):
    exercise_map = {
        0: 1.2,
        1: 1.375,
        2: 1.4625,
        3: 1.55,
        4: 1.725,
        5: 1.9
    }

    sex_correction = {
        "M": 5,
        "F": -161
    }

    age = (datetime.today() - birthday).days / 365
    BMR = 10 * weight + 6.25 * height - 5 * age
    print(BMR, sex_correction[sex])
    return (BMR + sex_correction[sex]) * exercise_map[exercise_level]

height = df_info["height"].values[0]
birthday = pd.to_datetime(df_info["birthday"].values[0])
sex = df_info["sex"].values[0]

st.write("### Today's Energy Overview")
exercise_level = st.slider("Exercise Level", min_value=0, max_value=5, value=2, step=1)
st.write("""
| Activity Level | Description                                      | BMR Multiplication Factor |
|----------------|--------------------------------------------------|---------------------------|
| 0              | Sedentary: little or no exercise                 | 1.200                     |
| 1              | Exercise 1-3 times/week                          | 1.375                     |
| 2              | Exercise 4-5 times/week                          | 1.465                     |
| 3              | Daily exercise or intense exercise 3-4 times/week| 1.550                     |
| 4              | Intense exercise 6-7 times/week                  | 1.725                     |
| 5              | Very intense exercise daily, or physical job     | 1.900                     |
""")

current_weight = float(df_weight_log["weight"].values[-1])
capacity = calculate_energy_burned(current_weight, height, birthday, exercise_level, sex)
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
    st.markdown(f"<span style='font-weight:bold'>Allowed: {round(capacity)} kcal </span>", unsafe_allow_html=True)
    st.markdown(f"<span style='color:green; font-weight:bold'>Remaining: {round(float(remaining.values[0]))} kcal </span>", unsafe_allow_html=True)
    colors = ("#d66154", "#dbd5ba", "#48ab8a", "#8db6c3", "#898989")
    colors = ("#bababa", "#9f9f9f", "#616161", "#4b4b4b", "#209253")
else:
    st.write(f"#### Oh No!", unsafe_allow_html=True)
    st.markdown(f"<span style='font-weight:bold'>Consumed: {round(consumed.to_list()[0])} kcal </span>", unsafe_allow_html=True)
    st.markdown(f"<span style='font-weight:bold'>Allowed: {round(capacity)} kcal </span>", unsafe_allow_html=True)
    st.markdown(f"<span style='color:red'>You have exceeded your daily calorie intake by {round(-remaining.values[0])} kcal</span>", unsafe_allow_html=True)
    colors = ("#d66154", "#dbd5ba", "#48ab8a", "#8db6c3", "#dd2e44")
    colors = ("#bababa", "#9f9f9f", "#616161", "#4b4b4b", "#ab3f3f")
st.bar_chart(calories_by_meal, horizontal=True, color=colors)

if st.button("Refresh Data"):
    st.rerun()

st.divider()

df_breakfast = df_day[df_day["meal"]=="Breakfast"]
df_lunch = df_day[df_day["meal"]=="Lunch"]
df_dinner = df_day[df_day["meal"]=="Dinner"]
df_snack = df_day[df_day["meal"]=="Snack"]

meals = [
    ("🍌", "Breakfast", df_breakfast),
    ("🥗", "Lunch", df_lunch),
    ("🥗", "Dinner", df_dinner),
    ("🍙", "Snack", df_snack)
]

for icon, meal, df in meals:
    st.write(f"### {icon} {meal}")
    st.dataframe(df[["Food", "Quantity", "Serving", "Calories"]])
    st.write(f"###### Total Calories: {df['Calories'].sum()} kcal")

    with st.expander(f"Add or Remove {meal} Food Log"):
        selection = st.pills("Mode", options=["Add Food", "Remove Food"],selection_mode="single", key=f"mode_{meal}", default="Add Food")
        if selection == "Add Food":
            st.write("### Add Food")
            col1, col2, col3 = st.columns(3)
            with col1:
                name = st.selectbox("Food Name", options=df_food_data.sort_values(by="Name")["Name"], key=f"name_{meal}", placeholder="Select Food", label_visibility="hidden")
            with col2:
                quantity = st.number_input("Servings", min_value=0., step=0.01, value=1.0, key=f"quantity_{meal}", label_visibility="hidden")
            with col3:
                serving = st.selectbox("Serving Type", options=[df_food_data.loc[df_food_data["Name"] == name, "Serving Name"].values[0], "g"], key=f"serving+{meal}", label_visibility="hidden")
            if serving == "g":
                # quantity = st.number_input("Quantity (g)", min_value=0, step=1, value=100, key=f"quantity_{meal}")
                weight = quantity
            else:
                # quantity = st.number_input("Servings", min_value=0., step=0.01, value=1.0, key=f"quantity_{meal}")
                weight = (quantity * df_food_data[df_food_data["Name"]==name]["Single Serving (g)"]).values[0]

            kcal_per_100g = df_food_data[df_food_data["Name"]==name]["Calories (kcal)"].values[0]
            kcal = (kcal_per_100g * weight) / 100
            st.write(" ")
            # st.write(" ")
            st.write(f"**Weight: ", weight, " g**")
            st.write(f"**Calories: ", kcal, " kcal**")
                # st.write(quantity, serving, " of ", name)
                # st.write("\t * ", weight, "g")
                # st.write("\t * ", kcal, "kcal")

            if st.button("Add Food", key=f"button_{meal}"):
                new_row = {
                    "date": date,
                    "meal": meal,
                    "name": name,
                    "quantity": quantity,
                    "serving": serving,
                }
                df_food_log = pd.concat([df_food_log, pd.DataFrame([new_row])], ignore_index=True)

                gsheets.update_google_sheet(
                    sheet_name=f"food_log_{who.lower()}",
                    updated_data=df_food_log
                )
                st.success("Food log added successfully!")
                st.rerun()
        elif selection == "Remove Food":
            st.write("### Remove Food")
            df["entry"] = df.index.astype(str) + ": " + df["Food"] + ", " + df["Quantity"].astype(str) + " " + df["Serving"].astype(str)
            food_to_remove = st.selectbox("Food Name", options=df["entry"], key=f"remove_{meal}")

            if st.button("Remove Food", key=f"remove_button_{meal}") and food_to_remove:
                food_name = food_to_remove.split(":")[1].split(",")[0].strip()
                food_quantity = float(food_to_remove.split(",")[1].split(" ")[1])

                df_remove = df_food_log[df_food_log["date"]==date]
                df_remove = df_remove[df_remove["meal"]==meal]
                df_remove = df_remove[df_remove["name"]==food_name]
                df_food_log = df_food_log.drop(df_remove.index)

                gsheets.update_google_sheet(
                    sheet_name=f"food_log_{who.lower()}",
                    updated_data=df_food_log
                )

                st.success("Food log removed successfully!")
                st.rerun()
