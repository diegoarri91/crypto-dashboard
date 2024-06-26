import plotly.express as px
import streamlit as st


st.title("Real-Time / Live Data Science Dashboard")

placeholder = st.empty()

with placeholder.container():
    fig = px.density_heatmap(
        data_frame=df, y="age_new", x="marital"
    )
