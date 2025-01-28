import streamlit as st
import pandas as pd
import numpy as np
from datetime import datetime
from google_sheets import GoogleSheetsInterface
import plotly.express as px
from scipy.interpolate import make_interp_spline, splrep, splev

gsheets = GoogleSheetsInterface()

st.set_page_config(page_title="Weight Overview", page_icon="🐖")

st.markdown("# Weight Overview 🐖")
st.write("View and log your weight.")

who = st.pills("Who", options=["Bela", "Marleen"], default="Bela", selection_mode="single")
df_weight_log = gsheets.load_google_sheet_data(sheet_name=f"weight_log_{who.lower()}")

current_weight = float(df_weight_log["weight"].values[-1])

df_weight_log["moving_average"] = df_weight_log["weight"].rolling(window=3, min_periods=1).mean()

df = df_weight_log.rename(columns={"date": "Date", "weight": "Weight (kg)", "moving_average": "Weight Moving Average (kg)"})

df_weight_log_plot = df_weight_log.copy()
df_weight_log_plot = df_weight_log_plot.sort_values(by="date")

x = pd.to_datetime(df_weight_log_plot["date"])
y = df_weight_log_plot["weight"]
y_avg = df_weight_log_plot["moving_average"]

tck = splrep(x, y_avg, s=3)
x_smooth = x
y_smooth = splev(x_smooth, tck, der=0)


plot = px.scatter(df_weight_log_plot, x="date", y="weight", labels={"weight": "Weight (kg)"}, color_discrete_sequence=["#ff4b4b"])
plot.add_scatter(x=x_smooth, y=y_smooth, mode="lines", name="Moving Average")

minval = int(df_weight_log_plot["weight"].min()-1.5)
maxval = int(df_weight_log_plot["weight"].max()+1.5)

plot.update_yaxes(range=[minval, maxval])

st.plotly_chart(plot, use_container_width=True)

st.write(df)



st.write(f"### Log Weight")
mode = st.pills("Mode", ["Add", "Remove"], default="Add", selection_mode="single")
if mode == "Add":
    df_weight_log = df_weight_log[["date", "weight"]]
    date = st.date_input("Date", value=datetime.today().date())
    weight = st.slider("Weight (kg)", min_value=current_weight-5, max_value=current_weight+5, value=current_weight, step=0.1)
    # weight = st.number_input("Weight (kg)", min_value=current_weight, step=0.1)

    new_row = {
        "date": date.strftime("%Y-%m-%d"),
        "weight": weight
    }
    df_weight_log = pd.concat([df_weight_log, pd.DataFrame([new_row])], ignore_index=True)

    if st.button("Add Weight"):
        st.write("updated data:")
        st.dataframe(df_weight_log.tail(1))

        gsheets.update_google_sheet(
            sheet_name=f"weight_log_{who.lower()}",
            updated_data=df_weight_log
        )
        st.success("Weight log added successfully!")
        st.rerun()


elif mode == "Remove":
    date = st.date_input("Date", value=datetime.today().date())
    df_to_remove = df_weight_log[df_weight_log["date"] == date.strftime("%Y-%m-%d")]
    st.write(df_to_remove)

    weight = st.selectbox("Select weight entry to remove", df_to_remove["weight"].values)
    # weight = st.number_input("Weight (kg)", min_value=current_weight, step=0.1)

    if st.button("Remove Weight"):
        df_weight_log = df_weight_log[~((df_weight_log["date"] == date.strftime("%Y-%m-%d")) & (df_weight_log["weight"] == weight))]

        gsheets.update_google_sheet(
            sheet_name=f"weight_log_{who.lower()}",
            updated_data=df_weight_log
        )

        st.success("Weight log removed successfully!")
        st.rerun()
