import streamlit as st
import time
import numpy as np

st.set_page_config(page_title="Food Logger", page_icon="🍔")

st.markdown("# Food Logger 🍔")
st.sidebar.header("Food Logger")
st.write(
    """
    Log Food and Calorie Intake
    """
)

# Streamlit widgets automatically run the script from top to bottom. Since
# this button is not connected to any other logic, it just causes a plain
# rerun.
st.button("Re-run")
