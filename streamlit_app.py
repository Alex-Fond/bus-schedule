import streamlit as st
import pandas as pd
import time
import datetime
import math
import json



# The functions to actually check stuff
def safety_margin(activity):
    bus = int(str(df_schedule.loc[df_schedule["activity_number"] == activity, "bus_number"]).split()[1])
    battery = float(str(df_schedule.loc[df_schedule["activity_number"] == activity, "battery"]).split()[1])
    string = f"bus_{bus}_soh"
    soh = bus_settings[string]
    battery_minimum = minimum_soc
    battery_maximum = maximum_soc
    if battery < battery_minimum * soh:
        st.write(f"Error: Bus {bus} reaches below required minimum battery charge during activity {activity}")
        return False
    elif battery > battery_maximum * soh:
        st.write(f"Error: Bus {bus} above required maximum battery charge during activity {activity}")
        return False
    return True

def calc_battery(activity):
    start = str(df_schedule.loc[df_schedule["activity_number"] == activity, "start_time_long"]).split()[1]
    end = str(df_schedule.loc[df_schedule["activity_number"] == activity, "end_time_long"]).split()[1]
    bus = int(str(df_schedule.loc[df_schedule["activity_number"] == activity, "bus_number"]).split()[1])
    time_delta = datetime.timedelta(end-start).total_seconds/3600
    string = f"bus_{bus}_custom_usage"
    if bus_settings[string] == True:
        usage = float(str(df_schedule.loc[df_schedule["activity_number"] == activity, "usage"]).split()[1])
    else:
        print("hello world hi 1 2 3".split()[1:-3])
        act = str(df_schedule.loc[df_schedule["activity_number"] == activity, "activity"]).split()[1]

# Full schedule check
def check_schedule():
    global progress_max, progress_current, check_progress
    progress_max = len(df_schedule.index) + len(df_timetable.index)
    progress_current = 0
    check_progress = st.progress(progress_current)
    df_schedule["battery"] = 0
    df_timetable["satisfied"] = 0
    df_timetable["index"] = range(len(df_timetable.index))
    for activity in df_schedule.sort_values(by="start_time_long")["activity_number"]:
        #calc_battery(activity)
        progress_current += 1
        check_progress.progress(progress_current/progress_max)
    check_timetable()

# Full timetable check
def check_timetable():
    global progress_max, progress_current, check_progress
    for index in df_timetable["index"]:
        progress_current += 1
        check_progress.progress(progress_current/progress_max)



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
    maximum_soc = st.number_input("Maximum State of Charge (0-1)", value=0.9, min_value=max(0., minimum_soc), max_value=1., step=0.05)
    st.write("Charging")
    optimal_charge = st.slider("Optimal battery range for charging (0-1)", value=(0.0, 0.9), min_value=0., max_value=1., step=0.01)
    charge_speed_optimal = st.number_input("Charging speed within optimal battery range (kWh)", value=450., min_value=0., step=10.)
    charge_speed_suboptimal = st.number_input("Charging speed outside optimal battery range (kWh)", value=60., min_value=0., step=10.)
    min_charge_time = st.number_input("Minimum charge time (minutes)", value=15., min_value=0., step=5.)
    st.write("Default schedule settings")
    st.write(":red[Warning: changing these settings below will reset their respective values in your schedule settings!]")
    default_battery = st.number_input("Default battery capacity at 100% State of Health (kWh)", value=100., min_value=0., step=10.)
    default_battery_start = st.number_input("Default battery percentage at the start of the schedule", value=1., min_value=0., max_value=1., step=0.01)
    default_soh = st.number_input("Default State of Health (0-1)", value=0.85, min_value=0., max_value=1., step=0.05)
    default_idle = st.number_input("Default usage (kWh) - idle", value=0.01, min_value=0., step=0.01)
    default_active = st.number_input("Default usage (kWh) - active", value=10.8, min_value=0., step=1.)
    default_custom_usage = st.checkbox("By default use usage values in imported Excel sheet instead of these settings")

with st.popover("Open schedule settings"):
    if uploaded_schedule is not None:
        st.subheader("Activity settings")
        idle_name = st.text_input("Activity name - idling", value="idle")
        charge_name = st.text_input("Activity name - charging", value="charging")
        ignore_charge_name = st.checkbox("Ignore set charging name and instead use negative usage :red[(requires custom usage values to be turned on)]")
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
            bus_string = f"bus_{i+1}_custom_usage"
            bus_settings[bus_string] = st.checkbox(f"Bus {i+1} - use usage values in imported Excel sheet instead of these settings", value=default_custom_usage)
            bus_string = f"bus_{i+1}_battery_max"
            bus_settings[bus_string] = st.number_input(f"Bus {i+1} - battery capacity at 100% State of Health (kWh)", value=default_battery, min_value=0., step=10.)
            bus_string = f"bus_{i+1}_battery_start"
            bus_settings[bus_string] = st.number_input(f"Bus {i+1} - battery percentage at the start of the schedule", value=default_battery_start, min_value=0., max_value=1., step=0.01)
    else:
        st.write("Please upload a schedule first.")

with st.expander("How to use"):
    st.write("Upload a planning with busses and a timetable of all bus rides that need to be accounted for, following the format specified in the user manual.")
    st.write("Change the tool settings and schedule settings, using the information in the user manual. Percentages are measured from 0-1 rather than 0%-100%.")
    st.write("Once the Excel files are uploaded and the settings are adjusted correctly, click the \"Check uploaded bus schedule\" button to verify the validity of the uploaded schedule.")
