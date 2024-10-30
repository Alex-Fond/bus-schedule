import streamlit as st
import pandas as pd
import time
import datetime
import math
import json



# The functions to actually check stuff
def check_schedule():
    return



st.title("My app")
st.write(
    "For help and documentation, head over to [docs.streamlit.io](https://docs.streamlit.io/)."
)

uploaded_schedule = st.file_uploader("Upload bus schedule (Excel)", type="xlsx")

if uploaded_schedule is not None:
    global df_schedule, bus_count
    df_schedule = pd.read_excel(uploaded_schedule, names=["activity_number", "start_location", "end_location", "start_time", "end_time", "activity", "bus_line", "energy_usage", "start_time_long", "end_time_long", "bus_number"])
    st.write(uploaded_schedule.name)
    bus_count = df_schedule["bus_number"].nunique()

uploaded_distances = st.file_uploader("Upload timetable to satisfy (Excel)", type="xlsx")

if uploaded_distances is not None:
    global df_timetable
    df_timetable = pd.read_excel(uploaded_distances, names=["start_location", "start_time", "end_location", "bus_line"])
    st.write(uploaded_distances.name)

if st.button("Check uploaded bus schedule") and uploaded_schedule != None and uploaded_distances != None:
    st.write(df_schedule.head())
    st.write(df_timetable.head())
    check_schedule()

with st.popover("Open tool settings"):
    st.write("State of Health")
    minimum_soc = st.number_input("Minimum State of Charge (0-1)", value=0.1, min_value=0., max_value=1., step=0.05)
    maximum_soc = st.number_input("Maximum State of Charge (0-1)", value=0.9, min_value=0., max_value=1., step=0.05)
    st.write("Charging")
    optimal_charge = st.number_input("Optimal battery range for charging (0-1)", value=(0.0, 0.9), min_value=0., max_value=1., step=0.05)
    charge_speed_optimal = st.number_input("Charging speed within optimal battery range (kWh)", value=450, min_value=0., step=10.)
    charge_speed_suboptimal = st.number_input("Charging speed outside optimal battery range (kWh)", value=60, min_value=0., step=10.)
    st.write("Other settings")
    use_custom_usage = st.checkbox("Use usage values in imported Excel sheet instead of these settings")
    st.write("Default schedule settings")
    st.write(":red[Warning: changing these settings below will reset their respective values in your schedule settings!]")
    default_soh = st.number_input("Default State of Health (0-1)", value=0.85, min_value=0., max_value=1., step=0.05)
    default_idle = st.number_input("Default usage (kWh) - idle", value=0.01, min_value=0., step=0.01)
    default_active = st.number_input("Default usage (kWh) - active", value=10.8, min_value=0., step=1.)

with st.popover("Open schedule settings"):
    if uploaded_schedule is not None:
        st.subheader("Schedule settings")
        active_name = st.text_input("Activity name - actively transporting passengers", value="transport")
        idle_name = st.text_input("Activity name - idling", value="idle")
        charge_name = st.text_input("Activity name - charging", value="charging")
        ignore_charge_name = st.checkbox("Ignore set charging name and instead use negative usage (requires custom usage values to be turned on)")
        st.subheader("Bus settings")
        st.write(":red[You can change these default values in your tool settings.]")
        global bus_settings
        bus_settings = json.loads("{}")
        for i in range(bus_count):
            st.write(f"Bus {i+1}")
            bus_string = f"bus_{i+1}_soh"
            bus_settings[bus_string] = st.number_input(f"Bus {i+1} - State of Health", value=default_soh, min_value=0., max_value=1., step=0.05)
            bus_string = f"bus_{i+1}_idle"
            bus_settings[bus_string] = st.number_input(f"Bus {i+1} - Usage (kWh) - idle", value=default_idle, min_value=0., step=0.1)
            bus_string = f"bus_{i+1}_active"
            bus_settings[bus_string] = st.number_input(f"Bus {i+1} - Usage (kWh) - active", value=default_active, min_value=0., step=1.)
    else:
        st.write("Please upload a schedule first.")












st.title('st.progress example DELETEINFINALPRODUCT ##########################')

with st.expander('About this app'):
    st.write('You can now display the progress of your calculations in a Streamlit app with the `st.progress` command.')

my_bar = st.progress(0)

for percent_complete in range(100):
    time.sleep(0.05)
    my_bar.progress(percent_complete + 1)
