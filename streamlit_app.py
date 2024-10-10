import streamlit as st
import pandas as pd

st.title("My app")
st.write(
    "For help and documentation, head over to [docs.streamlit.io](https://docs.streamlit.io/)."
)

uploaded_file = st.file_uploader("Upload planning (Excel)", type="xlsx")
df_uploaded = pd.read_excel(uploaded_file)

st.write(uploaded_file.name)