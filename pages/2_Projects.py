import streamlit as st

from resume_shell import render_portfolio_chrome

st.set_page_config(
    page_title="Projects · Jack Druyon",
    page_icon=":material/folder_open:",
    layout="wide",
    initial_sidebar_state="collapsed",
)

render_portfolio_chrome(show_hero=False)

st.markdown(
    r"""
<style>
/* One white project card (keyed container + contents) */
section[data-testid="stMain"] [class*="st-key-elias_project_panel"],
section[data-testid="stMain"] div.st-key-elias_project_panel {
    background: #FFFFFF !important;
    border: 2px solid #0D0D0D !important;
    border-radius: 12px !important;
    padding: 28px 32px 32px !important;
    box-shadow: 0 3px 10px rgba(0, 0, 0, 0.05) !important;
    max-width: 720px;
    margin-left: auto !important;
    margin-right: auto !important;
}
section[data-testid="stMain"] .elias-proj-title {
    font-family: 'Playfair Display', 'Georgia', serif;
    font-size: 2.35rem !important;
    font-weight: 700 !important;
    line-height: 1.15 !important;
    color: #0D0D0D !important;
    margin: 0 0 16px 0 !important;
    letter-spacing: 0.02em !important;
}
section[data-testid="stMain"] .elias-proj-sub {
    font-size: 0.7rem !important;
    font-weight: 700 !important;
    letter-spacing: 0.2em !important;
    text-transform: uppercase !important;
    color: #444 !important;
    margin: 0 0 20px 0 !important;
}
section[data-testid="stMain"] .elias-proj-body {
    font-size: 1.05rem !important;
    line-height: 1.65 !important;
    color: #1a1a1a !important;
    margin: 0 0 28px 0 !important;
}
section[data-testid="stMain"] .elias-proj-hint {
    font-size: 0.82rem !important;
    line-height: 1.45 !important;
    color: #555 !important;
    margin: 16px 0 0 0 !important;
}
section[data-testid="stMain"] .elias-proj-tech {
    font-size: 0.88rem !important;
    line-height: 1.55 !important;
    color: #333 !important;
    margin: 20px 0 0 0 !important;
    padding-top: 18px !important;
    border-top: 1px solid #e8e8e8 !important;
}
section[data-testid="stMain"] .elias-proj-tech strong {
    color: #0D0D0D !important;
    font-weight: 600 !important;
}
section[data-testid="stMain"] .elias-proj-tech ul {
    margin: 10px 0 0 0 !important;
    padding-left: 1.2rem !important;
}
section[data-testid="stMain"] .elias-proj-tech li {
    margin-bottom: 6px !important;
}
/* Obvious “take me there” control: white fill, hard black frame */
section[data-testid="stMain"] [class*="st-key-elias_project_panel"] button[data-testid="baseButton-primary"],
section[data-testid="stMain"] [class*="st-key-elias_project_panel"] [data-testid="stBaseButton-primary"],
section[data-testid="stMain"] div.st-key-elias_project_panel button[data-testid="baseButton-primary"] {
    width: 100% !important;
    min-height: 6.25rem !important;
    padding: 1.35rem 1.5rem !important;
    border-radius: 10px !important;
    background: #FFFFFF !important;
    background-image: none !important;
    color: #0D0D0D !important;
    border: 3px solid #0D0D0D !important;
    box-shadow: 3px 3px 0 #0D0D0D !important;
    font-size: 2.05rem !important;
    font-weight: 700 !important;
    letter-spacing: 0.03em !important;
    text-transform: none !important;
    transition: transform 0.12s ease, box-shadow 0.12s ease !important;
}
section[data-testid="stMain"] [class*="st-key-elias_project_panel"] button[data-testid="baseButton-primary"]:hover,
section[data-testid="stMain"] div.st-key-elias_project_panel button[data-testid="baseButton-primary"]:hover {
    transform: translate(1px, 1px) !important;
    box-shadow: 2px 2px 0 #0D0D0D !important;
    filter: none !important;
    background: #FAFAFA !important;
}
section[data-testid="stMain"] [class*="st-key-elias_project_panel"] button[data-testid="baseButton-primary"] p,
section[data-testid="stMain"] [class*="st-key-elias_project_panel"] button[data-testid="baseButton-primary"] span,
section[data-testid="stMain"] [class*="st-key-elias_project_panel"] [data-testid="stBaseButton-primary"] p,
section[data-testid="stMain"] [class*="st-key-elias_project_panel"] [data-testid="stBaseButton-primary"] span {
    color: #0D0D0D !important;
    font-size: 2.05rem !important;
    line-height: 1.2 !important;
}
/* Fallback if keyed class name differs in your Streamlit build */
section[data-testid="stMain"] [data-testid="stVerticalBlockBorderWrapper"]:has(.elias-proj-title) {
    background: #FFFFFF !important;
    border: 2px solid #0D0D0D !important;
    border-radius: 12px !important;
    padding: 24px 28px 28px !important;
    box-shadow: 0 3px 10px rgba(0, 0, 0, 0.05) !important;
    max-width: 720px;
    margin-left: auto !important;
    margin-right: auto !important;
}
section[data-testid="stMain"] [data-testid="stVerticalBlockBorderWrapper"]:has(.elias-proj-title) button[data-testid="baseButton-primary"] {
    width: 100% !important;
    min-height: 6.25rem !important;
    padding: 1.35rem 1.5rem !important;
    border-radius: 10px !important;
    background: #FFFFFF !important;
    background-image: none !important;
    color: #0D0D0D !important;
    border: 3px solid #0D0D0D !important;
    box-shadow: 3px 3px 0 #0D0D0D !important;
    font-size: 2.05rem !important;
    font-weight: 700 !important;
    letter-spacing: 0.03em !important;
}
section[data-testid="stMain"] [data-testid="stVerticalBlockBorderWrapper"]:has(.elias-proj-title) button[data-testid="baseButton-primary"]:hover {
    transform: translate(1px, 1px) !important;
    box-shadow: 2px 2px 0 #0D0D0D !important;
}
section[data-testid="stMain"] [data-testid="stVerticalBlockBorderWrapper"]:has(.elias-proj-title) button[data-testid="baseButton-primary"] p,
section[data-testid="stMain"] [data-testid="stVerticalBlockBorderWrapper"]:has(.elias-proj-title) button[data-testid="baseButton-primary"] span {
    color: #0D0D0D !important;
    font-size: 2.05rem !important;
    line-height: 1.2 !important;
}
</style>
""",
    unsafe_allow_html=True,
)

with st.container(border=True, key="elias_project_panel", gap="medium"):
    st.markdown(
        """
<div>
  <p class="elias-proj-sub">Disney sentiment · Guest intelligence</p>
  <h2 class="elias-proj-title">Elias Intelligence</h2>
  <p class="elias-proj-body">
    Disney Sentiment Tool, Python/SQL pipeline that scrapes and analyzes unfiltered guest Reddit
    feedback to surface actionable experience insights for Disney Experiences &lsquo;Elias&rsquo;.
  </p>
</div>
""",
        unsafe_allow_html=True,
    )
    if st.button(
        "Take me to the Elias Dashboard",
        type="primary",
        key="elias_launch_cta",
        width="stretch",
        help="Opens the Elias dashboard: briefings, charts, and search.",
    ):
        st.switch_page("pages/4_Elias_Intelligence.py")
    st.markdown(
        """
<div class="elias-proj-tech">
  <p><strong>Technical overview</strong></p>
  <p>
    Elias runs on a Python scraping script that collects guest discussion data, stores that data in Supabase
    using a Supabase API integration. A ChatGPT API (OpenAI) powers
    LLM filtering and structured scoring of raw comments before they become insights. It is meant to distill guest feedback into actionable insights.
    The experience layer is app development in Streamlit: data visualization,
    dashboards, and a search bar feature over the insight corpus. The stack is
    hosted on Railway, with source and deployment flow managed through GitHub.
  </p>
  <p style="margin-top:12px;margin-bottom:6px;"><strong>Key tools</strong></p>
  <ul>
    <li>LLM filtering</li>
    <li>Data scraping</li>
    <li>Data storage</li>
    <li>Data visualization</li>
    <li>Search bar feature</li>
    <li>App development</li>
    <li>Web hosting</li>
  </ul>
</div>
""",
        unsafe_allow_html=True,
    )
    st.markdown(
        '<p class="elias-proj-hint">Loads the live application in this workspace. Use the host '
        "navigation or browser back to return to the portfolio when you&rsquo;re done.</p>",
        unsafe_allow_html=True,
    )
