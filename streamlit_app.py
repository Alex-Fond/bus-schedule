import streamlit as st
import pandas as pd

st.title("🎈 My new app")
st.write(
    "Let's start building! For help and inspiration, head over to [docs.streamlit.io](https://docs.streamlit.io/)."
)

uploaded_file = st.file_uploader("Upload planning (Excel)", type="xlsx")
df_uploaded = pd.read_excel(uploaded_file)

st.write(df_uploaded.head())