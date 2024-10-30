import streamlit as st
import pandas as pd
import time
import json



# The fnctions to actually check stuff
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
    # Schedule checking function

with st.popover("Open tool settings"):
    st.write("Minimum State of Charge (0-1)")
    minimum_soc = st.number_input("num test", value=0.1, min_value=0., max_value=1., step=0.05)
    st.write("Maximum State of Charge (0-1)")
    maximum_soc = st.number_input("num test", value=0.9, min_value=0., max_value=1., step=0.05)
    st.subheader("Warning: changing the below settings will reset their respective schedule settings!")
    st.write("Default State of Health (0-1)")
    default_soh = st.number_input("num test", value=0.85, min_value=0., max_value=1., step=0.05)
    st.write("Default usage (kWh) - idle")
    default_idle = st.number_input("num test", value=0.1, min_value=0., step=0.1)
    st.write("Default usage (kWh) - driving")
    default_active = st.number_input("num test", value=10., min_value=0., step=1.)

with st.popover("Open schedule settings"):
    if uploaded_schedule is not None:
        global bus_settings
        bus_settings = json.loads("{}")
        for i in range(bus_count):
            st.write(f"Bus {i+1}")
            bus_string = f"bus_{i+1}_soh"
            bus_settings[bus_string] = st.number_input(f"Bus {i+1} - State of Health", value=default_soh, min_value=0., max_value=1., step=0.05)
            bus_string = f"bus_{i+1}_idle"
            bus_settings[bus_string] = st.number_input(f"Bus {i+1} - Usage (kWh) - idle", value=default_idle, min_value=0., step=0.1)
            bus_string = f"bus_{i+1}_active"
            bus_settings[bus_string] = st.number_input(f"Bus {i+1} - Usage (kWh) - driving", value=default_active, min_value=0., step=1.)
    else:
        st.write("Please upload a schedule first.")












st.title('st.progress example')

with st.expander('About this app'):
    st.write('You can now display the progress of your calculations in a Streamlit app with the `st.progress` command.')

my_bar = st.progress(0)

for percent_complete in range(100):
    time.sleep(0.05)
    my_bar.progress(percent_complete + 1)
