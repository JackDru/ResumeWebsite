import streamlit as st

from resume_shell import render_portfolio_chrome

st.set_page_config(
    page_title="Contact · Jack Druyon",
    page_icon=":material/mail:",
    layout="wide",
    initial_sidebar_state="collapsed",
)

render_portfolio_chrome(show_hero=False)

st.markdown(
    """
<div class="portfolio-card">
  <h2>Contact</h2>
  <p>
    For professional inquiries, collaborations, or a copy of my resume, please use one of the
    channels below.
  </p>
  <div class="contact-line"><strong>SchoolEmail</strong> druyonj@byu.edu</div>
  <div class="contact-line"><strong>Personal Email</strong> druyonjack87@gmail.com</div>
  <div class="contact-line"><strong>Phone</strong> (385) 267-90**</div>
  <div class="contact-line"><strong>LinkedIn</strong> www.linkedin.com/in/jack-druyon-4a7a052a4</div>
  <div class="contact-line"><strong>GitHub</strong> github.com/JackDru</div>
  <div class="contact-line"><strong>Location</strong> Bountiful, UT</div>
</div>
""",
    unsafe_allow_html=True,
)
