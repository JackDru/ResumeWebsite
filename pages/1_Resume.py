import base64
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

    b64 = base64.b64encode(pdf_bytes).decode()
    st.markdown(
        f'<iframe src="data:application/pdf;base64,{b64}" width="100%" height="900px" type="application/pdf"></iframe>',
        unsafe_allow_html=True,
    )
else:
    st.warning(
        "Resume PDF not found. Add the file as **assets/resume.pdf** in the project root "
        "so it can be shown here and downloaded as **Druyon, Jack.pdf**."
    )
