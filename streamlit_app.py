import streamlit as st
import pandas as pd
import time
import datetime
import math
import json
import numpy as np
import matplotlib.pyplot as plt

# The functions to actually check stuff
def safety_margin(activity):
    with open('bus.json') as f:
        bus_settings = json.load(f)
    with open('tool.json') as f:
        tool_settings = json.load(f)
    bus = int(str(df_schedule.loc[df_schedule["activity_number"] == activity, "bus_number"]).split()[1:-4])
    battery = float(str(df_schedule.loc[df_schedule["activity_number"] == activity, "battery"]).split()[1:-4])
    string = f"bus_{bus}_soh"
    soh = bus_settings[string]
    battery_minimum = tool_settings["minimum_soc"]
    battery_maximum = tool_settings["maximum_soc"]
    if battery * soh < battery_minimum:
        st.write(f":red[Error]: Bus {bus} reaches below required minimum battery charge during activity {activity}")
        return False
    elif battery * soh > battery_maximum:
        st.write(f":red[Error]: Bus {bus} above required maximum battery charge during activity {activity}")
        return False
    return True

def validate_times():
    with open('bus.json') as f:
        bus_settings = json.load(f)
    with open('tool.json') as f:
        tool_settings = json.load(f)
    for activity in df_schedule["activity_number"]:
        timespan = calc_time_activity(activity)
        if timespan < 0:
            timespan = 0
            st.write(f":red[Error]: activity {activity} ends before it starts (negative duration), activity ignored")
        elif timespan == 0:
            st.write(f":orange[Warning]: activity {activity} ends at the same time as it starts (duration of 0), activity ignored")

###############################################################################################################################################################
def calc_battery(activity):
    with open('bus.json') as f:
        bus_settings = json.load(f)
    with open('tool.json') as f:
        tool_settings = json.load(f)
    timespan = calc_time_activity(activity)
    bus = int(str(df_schedule.loc[df_schedule["activity_number"] == activity, "bus_number"]).split()[1:-4])
    string = f"bus_{bus}_custom_usage"
    if bus_settings[string] == True:
        usage = float(str(df_schedule.loc[df_schedule["activity_number"] == activity, "usage"]).split()[1:-4])
    else:
        act = str(df_schedule.loc[df_schedule["activity_number"] == activity, "activity"]).split()[1:-4]

def calc_charging_speed(activity):
    with open('bus.json') as f:
        bus_settings = json.load(f)
    with open('tool.json') as f:
        tool_settings = json.load(f)
    bus = int(str(df_schedule.loc[df_schedule["activity_number"] == activity, "bus_number"]).split()[1:-4])
    string = f"bus_{bus}_custom_usage"
    if bus_settings[string] == True:
        return float(str(df_schedule.loc[df_schedule["activity_number"] == activity, "usage"]).split()[1:-4])
    else:
        battery = float(str(df_schedule.loc[df_schedule["activity_number"] == activity, "battery"]).split()[1:-4])
        if battery <= tool_settings["optimal_charge"][1] and battery >= tool_settings["optimal_charge"][0]:
            timetil = calc_time_until_perc(bus, battery, tool_settings["optimal_charge"][1], tool_settings["charge_speed_optimal"])
            timespan = calc_time_activity(activity)
            if timespan <= timetil:
                return tool_settings["charge_speed_optimal"]
            else:
                speed = ((timespan * tool_settings["charge_speed_optimal"]) + ((timetil-timespan) * tool_settings["charge_speed_suboptimal"])) / (timespan + timetil)
                return speed
        elif battery >= tool_settings["optimal_charge"][1]:
            return tool_settings["charge_speed_suboptimal"]
        elif battery <= tool_settings["optimal_charge"][0]:
            timetil = calc_time_until_perc(bus, battery, tool_settings["optimal_charge"][0], tool_settings["charge_speed_suboptimal"])
            timespan = calc_time_activity(activity)
            if timespan <= timetil:
                return tool_settings["charge_speed_suboptimal"]
            else:
                speed = ((timespan * tool_settings["charge_speed_suboptimal"]) + ((timetil-timespan) * tool_settings["charge_speed_optimal"])) / (timespan + timetil)
                return speed

def calc_time_until_perc(bus, battery, charge, charge_speed):
    with open('bus.json') as f:
        bus_settings = json.load(f)
    with open('tool.json') as f:
        tool_settings = json.load(f)
    string = f"bus_{bus}_soh"
    soh = bus_settings[string]
    string = f"bus_{bus}_battery_max"
    max_charge = bus_settings[string]
    dif = (charge - battery) * max_charge * soh
    timespan = dif/charge_speed
    return timespan

def calc_time_activity(activity):
    with open('bus.json') as f:
        bus_settings = json.load(f)
    with open('tool.json') as f:
        tool_settings = json.load(f)
    start_time_list = str(df_schedule.loc[df_schedule["activity_number"] == activity, "start_time_long"]).split()[1:-4]
    if len(start_time_list) == 1:
        start_time_list.append("00:00:00")
    start_time = start_time_list[0] + " " + start_time_list[1]
    end_time_list = str(df_schedule.loc[df_schedule["activity_number"] == activity, "end_time_long"]).split()[1:-4]
    if len(end_time_list) == 1:
        end_time_list.append("00:00:00")
    end_time = end_time_list[0] + " " + end_time_list[1]
    start = datetime.datetime(*time.strptime(start_time, "%Y-%m-%d %H:%M:%S")[0:6])
    end = datetime.datetime(*time.strptime(end_time, "%Y-%m-%d %H:%M:%S")[0:6])
    difference = end - start
    timespan = difference.total_seconds()/60/60
    return timespan

def calc_charge_time_minimum(activity):
    with open('bus.json') as f:
        bus_settings = json.load(f)
    with open('tool.json') as f:
        tool_settings = json.load(f)
    return calc_time_activity(activity) >= tool_settings["min_charge_time"]

def check_overlapping_activities(bus):
    with open('bus.json') as f:
        bus_settings = json.load(f)
    with open('tool.json') as f:
        tool_settings = json.load(f)
    return

def calc_dpru_dru():
    with open('bus.json') as f:
        bus_settings = json.load(f)
    with open('tool.json') as f:
        tool_settings = json.load(f)
    dpru = 0
    dru = 0
    for activity in df_schedule["activity_number"]:
        timespan = calc_time_activity(activity)
        if timespan < 0:
            timespan = 0
        dpru += timespan
        active = bus_settings["active_name"].split()
        if str(df_schedule.loc[df_schedule["activity_number"] == activity, "activity"]).split()[1:-4] == active:
            dru += timespan
    if dru == 0:
        st.write(f":red[Error]: no activities with name {bus_settings['active_name']} found with duration greater than 0")
        return 0
    return dpru/dru

# Full schedule check
def check_schedule():
    with open('bus.json') as f:
        bus_settings = json.load(f)
    with open('tool.json') as f:
        tool_settings = json.load(f)
    global progress_max, progress_current, check_progress
    progress_max = len(df_schedule.index) + len(df_timetable.index)
    progress_current = 0
    check_progress = st.progress(progress_current)
    df_schedule["battery"] = 0
    df_timetable["satisfied"] = 0
    df_timetable["index"] = range(len(df_timetable.index))
    errorless = True
    validate_times()
    for activity in df_schedule.sort_values(by="start_time_long")["activity_number"]:
        #calc_battery(activity)
        #erroring = safety_margin()
        #if errorless == True:
            #errorless = erroring
        progress_current += 1
        check_progress.progress(progress_current/progress_max)
    check_timetable()
    #if errorless == True:
        #chart()
    dpru_dru = calc_dpru_dru()
    if dpru_dru != 0:
        st.write(f"Calculated DPRU/DRU ratio: {dpru_dru}:1")

# Full timetable check
def check_timetable():
    with open('bus.json') as f:
        bus_settings = json.load(f)
    with open('tool.json') as f:
        tool_settings = json.load(f)
    global progress_max, progress_current, check_progress
    for index in df_timetable["index"]:
        progress_current += 1
        check_progress.progress(progress_current/progress_max)

# Create Gannt chart
def chart():
    with open('bus.json') as f:
        bus_settings = json.load(f)
    with open('tool.json') as f:
        tool_settings = json.load(f)
    fig, ax = plt.subplots(figsize=(20, 5))
    busses = []
    for i in range(len(df_schedule["bus_number"].nunique())):
        busses.append(f"Bus {i+1}")
    for bus in busses:
        ax.barh(int(bus[4:]), 0)
        prev_x = 0
        for activity in df_schedule[df_schedule.bus_number==bus[4:]].sort_values(by="start_date_long")["activity_number"]:
            start = str(df_schedule.loc[df_schedule["activity_number"] == activity, "start_time"]).split()[1:-4]
            end = str(df_schedule.loc[df_schedule["activity_number"] == activity, "end_time"]).split()[1:-4]
            color = str(df_orders_chart.loc[df_orders_chart["Order"] == order, "Color"]).split()[1]
            if color == "Yellow":
                color = "y"
            else:
                color = f"tab:{str(color).lower()}"
            ax.barh(int(machine[1:]), setup, left=prev_x, color="k")
            ax.barh(int(machine[1:]), process, left=prev_x+setup, color=color)
            prev_x = end
    ax.set_ylabel("Machine")
    ax.set_xlabel("Time")
    ax.set_title(file_name)
    ax.set_yticks(np.arange(len(machines))+1, labels=machines)
    ax.invert_yaxis()
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

uploaded_timetable = st.file_uploader("Upload timetable to satisfy (Excel)", type="xlsx")

if uploaded_timetable is not None:
    global df_timetable
    df_timetable = pd.read_excel(uploaded_timetable, names=["start_location", "start_time", "end_location", "bus_line"])
    st.write(uploaded_timetable.name)

if st.button("Check uploaded bus schedule") and uploaded_schedule != None and uploaded_timetable != None:
    st.write(df_schedule.head())
    st.write(df_timetable.head())
    check_schedule()

with st.popover("Open tool settings"):
    tool_settings = json.loads("{}")
    st.write("State of Charge")
    st.write(":red[Warning: if you set any bus to have a SoC outside of this range it will generate an error!]")
    tool_settings["minimum_soc"] = st.number_input("Minimum State of Charge (0-1)", value=0.1, min_value=0., max_value=1., step=0.05)
    tool_settings["maximum_soc"] = st.number_input("Maximum State of Charge (0-1)", value=0.9, min_value=max(0., tool_settings["minimum_soc"]), max_value=1., step=0.05)
    st.write("Charging")
    tool_settings["optimal_charge"] = st.slider("Optimal battery range for charging (0-1)", value=(0.0, 0.9), min_value=0., max_value=1., step=0.01)
    tool_settings["charge_speed_optimal"] = st.number_input("Charging speed within optimal battery range (kWh)", value=450., min_value=0., step=10.)
    tool_settings["charge_speed_suboptimal"] = st.number_input("Charging speed outside optimal battery range (kWh)", value=60., min_value=0., step=10.)
    tool_settings["min_charge_time"] = st.number_input("Minimum charge time (minutes)", value=15., min_value=0., step=5.)
    st.write("Default schedule settings")
    st.write(":red[Warning: changing these settings below will reset their respective values in your schedule settings!]")
    default_battery = st.number_input("Default battery capacity at 100% State of Health (kWh)", value=100., min_value=0., step=10.)
    default_battery_start = st.number_input("Default battery percentage at the start of the schedule", value=1., min_value=0., max_value=1., step=0.01)
    default_soh = st.number_input("Default State of Health (0-1)", value=0.85, min_value=0., max_value=1., step=0.05)
    default_idle = st.number_input("Default usage (kWh) - idle", value=0.01, min_value=0., step=0.01)
    default_active = st.number_input("Default usage (kWh) - active", value=10.8, min_value=0., step=1.)
    default_custom_usage = st.checkbox("By default use usage values in imported Excel sheet instead of these settings")
    with open('tool.json', 'w') as f:
        json.dump(tool_settings, f)

with st.popover("Open schedule settings"):
    if uploaded_schedule is not None:
        bus_settings = json.loads("{}")
        st.subheader("Activity settings")
        bus_settings["active_name"] = st.text_input("Activity name - active (for DPRU/DRU)", value="driving")
        bus_settings["idle_name"] = st.text_input("Activity name - idling", value="idle")
        bus_settings["charge_name"] = st.text_input("Activity name - charging", value="charging")
        bus_settings["ignore_charge_name"] = st.checkbox("Ignore set charging name and instead use negative usage :red[(requires custom usage values to be turned on)]")
        st.subheader("Bus settings")
        st.write(":red[You can change these default values in your tool settings.]")
        for i in range(bus_count):
            st.write(f"Bus {i+1}")
            bus_string = f"bus_{i+1}_soh"
            bus_settings[bus_string] = st.number_input(f"Bus {i+1} - State of Health", value=default_soh, min_value=0., max_value=1., step=0.05)
            bus_string = f"bus_{i+1}_battery_max"
            bus_settings[bus_string] = st.number_input(f"Bus {i+1} - battery capacity at 100% State of Health (kWh)", value=default_battery, min_value=0., step=10.)
            bus_string = f"bus_{i+1}_battery_start"
            bus_settings[bus_string] = st.number_input(f"Bus {i+1} - battery percentage at the start of the schedule", value=default_battery_start, min_value=0., max_value=1., step=0.01)
            bus_string = f"bus_{i+1}_idle"
            bus_settings[bus_string] = st.number_input(f"Bus {i+1} - Usage (kWh) - idle", value=default_idle, min_value=0., step=0.1)
            bus_string = f"bus_{i+1}_active"
            bus_settings[bus_string] = st.number_input(f"Bus {i+1} - Usage (kWh) - active", value=default_active, min_value=0., step=1.)
            bus_string = f"bus_{i+1}_custom_usage"
            bus_settings[bus_string] = st.checkbox(f"Bus {i+1} - use usage values in imported Excel sheet instead of these settings", value=default_custom_usage)
        with open('bus.json', 'w') as f:
            json.dump(bus_settings, f)
    else:
        st.write("Please upload a schedule first.")

with st.expander("How to use"):
    st.write("Upload a planning with busses and a timetable of all bus rides that need to be accounted for, following the format specified in the user manual.")
    st.write("Change the tool settings and schedule settings, using the information in the user manual. Percentages are measured from 0-1 rather than 0%-100%.")
    st.write("Once the Excel files are uploaded and the settings are adjusted correctly, click the \"Check uploaded bus schedule\" button to verify the validity of the uploaded schedule.")
