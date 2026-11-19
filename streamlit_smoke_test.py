import sys
import streamlit as st

st.set_page_config(
    page_title="Hackathon Deployment Test",
    page_icon="🚀"
)

st.title("Hackathon Deployment Test")

st.success("Streamlit is running successfully!")

st.write("Python version:", sys.version.split()[0])
st.write("Streamlit version:", st.__version__)

st.info("Deployment environment test completed.")