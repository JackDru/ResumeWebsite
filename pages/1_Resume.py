from pathlib import Path

import streamlit as st

from resume_shell import render_portfolio_chrome

st.set_page_config(
    page_title="Resume · Jack Druyon",
    page_icon=":material/description:",
    layout="wide",
    initial_sidebar_state="collapsed",
)

render_portfolio_chrome(show_hero=False)

ROOT = Path(__file__).resolve().parent.parent
PDF_PATH = ROOT / "assets" / "resume.pdf"
RESUME_PUBLIC_URL = "https://raw.githubusercontent.com/JackDru/ResumeWebsite/main/assets/resume.pdf"

st.markdown(
    """
<div class="portfolio-card">
  <h2>Resume</h2>
  <p>
    Review my Resume below or download the PDF for offline use.
    
  </p>
</div>
""",
    unsafe_allow_html=True,
)

if PDF_PATH.is_file():
    pdf_bytes = PDF_PATH.read_bytes()
    st.download_button(
        label="Download Druyon, Jack.pdf",
        data=pdf_bytes,
        file_name="Druyon, Jack.pdf",
        mime="application/pdf",
        type="primary",
        use_container_width=True,
    )
    st.link_button(
        "Open resume in browser",
        RESUME_PUBLIC_URL,
        use_container_width=True,
    )
    st.caption(
        "If your browser blocks inline PDF previews, use the open/download buttons above."
    )
else:
    st.warning(
        "Resume PDF not found. Add the file as **assets/resume.pdf** in the project root "
        "so it can be shown here and downloaded as **Druyon, Jack.pdf**."
    )
