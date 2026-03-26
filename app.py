import streamlit as st

from resume_shell import render_portfolio_chrome

st.set_page_config(
    page_title="Jack Druyon",
    page_icon=":material/person:",
    layout="wide",
    initial_sidebar_state="collapsed",
)

render_portfolio_chrome(show_hero=True)
