"""
Shared layout and theme for the portfolio (non-Elias) pages.
Elias uses its own stylesheet inside pages/4_Elias_Intelligence.py.
"""
from __future__ import annotations

import streamlit as st

THEME_SESSION = "portfolio_theme_is_dark"


def _qp_theme() -> str | None:
    t = st.query_params.get("theme")
    if isinstance(t, list):
        return t[0] if t else None
    return t


def hydrate_theme_from_url() -> None:
    """Apply theme from ?theme=dark|light when present; otherwise keep session (survives toggle)."""
    t = _qp_theme()
    if t == "dark":
        st.session_state[THEME_SESSION] = True
    elif t == "light":
        st.session_state[THEME_SESSION] = False
    elif THEME_SESSION not in st.session_state:
        st.session_state[THEME_SESSION] = False


def _push_theme_to_url() -> None:
    want = "dark" if st.session_state.get(THEME_SESSION, False) else "light"
    if _qp_theme() != want:
        st.query_params["theme"] = want


def is_dark() -> bool:
    """Read current theme. Do not mutate session here — the toggle owns THEME_SESSION after it mounts."""
    return bool(st.session_state.get(THEME_SESSION, False))


def theme_query_params() -> dict[str, str]:
    return {"theme": "dark" if is_dark() else "light"}


def render_portfolio_styles() -> None:
    """Inject CSS after nav/toggle (call after render_site_nav so THEME_SESSION is current)."""
    dark = is_dark()
    if dark:
        bg, fg, muted, card, border, accent = (
            "#121218",
            "#E8E8E4",
            "#9A9690",
            "#1A1A22",
            "#2E2E36",
            "#C41E3A",
        )
        alert_body = "#E8E8E4"
    else:
        bg, fg, muted, card, border, accent = (
            "#F4F2EE",
            "#1C1B1A",
            "#3D3B38",
            "#FFFFFF",
            "#D9D4CC",
            "#8B1E2F",
        )
        alert_body = "#1C1B1A"

    # Streamlit’s layout uses stMain / stAppViewContainer, not section.main — and in
    # “light” custom BG it often keeps light-theme (pale) text. Force dark copy in light mode.
    light_extra = ""
    if not dark:
        light_extra = f"""
/* Light mode: force dark foreground on Streamlit wrappers & widgets */
[data-testid="stAppViewContainer"],
[data-testid="stAppViewContainer"] .stVerticalBlock,
[data-testid="stAppViewContainer"] [data-testid="stVerticalBlock"] {{
    color: {fg} !important;
}}

section[data-testid="stMain"],
section[data-testid="stMain"] .block-container {{
    color: {fg} !important;
}}

section[data-testid="stMain"] p,
section[data-testid="stMain"] li,
section[data-testid="stMain"] .stMarkdown,
section[data-testid="stMain"] [data-testid="stCaptionContainer"],
section[data-testid="stMain"] [data-testid="stMarkdownContainer"] p,
section[data-testid="stMain"] [data-testid="stMarkdownContainer"] li,
section[data-testid="stMain"] [data-testid="stMarkdownContainer"] span {{
    color: {muted} !important;
}}

section[data-testid="stMain"] [data-testid="stWidgetLabel"] p,
section[data-testid="stMain"] [data-testid="stWidgetLabel"] span,
section[data-testid="stMain"] label,
section[data-testid="stMain"] [data-baseweb="typo-body-small"],
section[data-testid="stMain"] [data-baseweb="typo-label-small"] {{
    color: {fg} !important;
}}

/* Page links (nav + Elias link) */
section[data-testid="stMain"] a[data-testid="stPageLink-NavLink"],
section[data-testid="stMain"] button[data-testid="baseButton-pageLink"] {{
    color: {accent} !important;
}}

/* Primary actions: keep light text on filled button */
section[data-testid="stMain"] button[data-testid="baseButton-primary"] {{
    color: #FFFFFF !important;
}}
section[data-testid="stMain"] button[data-testid="baseButton-primary"] *,
section[data-testid="stMain"] button[data-testid="baseButton-primary"] p {{
    color: #FFFFFF !important;
}}
"""

    st.markdown(
        f"""
<style>
@import url('https://fonts.googleapis.com/css2?family=Playfair+Display:wght@400;600;700&family=DM+Sans:wght@300;400;500;600&display=swap');

html, body, .stApp {{
    background-color: {bg} !important;
    color: {fg} !important;
    font-family: 'DM Sans', sans-serif !important;
}}

.stApp {{
    color-scheme: {'dark' if dark else 'light'};
}}

#MainMenu, footer {{ visibility: hidden; }}
header {{ visibility: hidden; height: 0; }}
.stDeployButton {{ display: none; }}

section[data-testid="stSidebar"] {{ display: none; }}

.block-container {{
    padding-top: 2rem !important;
    padding-bottom: 3rem !important;
    max-width: 960px !important;
}}

/* Main content text (both themes) */
section[data-testid="stMain"] .block-container,
section[data-testid="stMain"] .block-container [data-testid="stMarkdownContainer"],
section[data-testid="stMain"] .block-container [data-testid="stMarkdownContainer"] p,
section[data-testid="stMain"] .block-container [data-testid="stMarkdownContainer"] li,
section[data-testid="stMain"] .block-container [data-testid="stMarkdownContainer"] span {{
    color: {muted} !important;
}}

section[data-testid="stMain"] .block-container label,
section[data-testid="stMain"] .block-container [data-testid="stWidgetLabel"] p,
section[data-testid="stMain"] .block-container .stMarkdown label {{
    color: {fg} !important;
}}

/* Page links */
section[data-testid="stMain"] a[data-testid="stPageLink-NavLink"],
section[data-testid="stMain"] button[data-testid="baseButton-pageLink"] {{
    color: {accent} !important;
}}

{light_extra}

.portfolio-brand {{
    font-family: 'Playfair Display', serif;
    font-size: 1.35rem;
    font-weight: 700;
    letter-spacing: 0.06em;
    color: {fg} !important;
    margin: 0;
    padding-top: 4px;
}}
.portfolio-brand span {{ color: {accent} !important; }}

.portfolio-hero h1 {{
    font-family: 'Playfair Display', serif;
    font-size: 2.75rem;
    font-weight: 700;
    letter-spacing: 0.02em;
    color: {fg} !important;
    margin: 0 0 12px 0;
    line-height: 1.15;
}}

.portfolio-hero .role {{
    font-size: 0.85rem;
    font-weight: 600;
    letter-spacing: 0.14em;
    text-transform: uppercase;
    color: {accent} !important;
    margin-bottom: 20px;
}}

.portfolio-hero p {{
    font-size: 1.05rem;
    line-height: 1.75;
    color: {muted} !important;
    max-width: 720px;
    margin: 0;
}}

.portfolio-card {{
    background: {card};
    border: 1px solid {border};
    border-radius: 4px;
    padding: 28px 32px;
    margin-top: 20px;
}}

.portfolio-card h2 {{
    font-family: 'Playfair Display', serif;
    font-size: 1.35rem;
    color: {fg} !important;
    margin: 0 0 16px 0;
}}

.portfolio-card p,
.portfolio-card li {{
    color: {muted} !important;
    line-height: 1.65;
}}

.contact-line {{
    margin-bottom: 14px;
    font-size: 0.98rem;
    color: {muted} !important;
}}
.contact-line strong {{
    color: {fg} !important;
    display: inline-block;
    min-width: 88px;
}}

.stMarkdown a {{ color: {accent} !important; }}

iframe {{ border: 1px solid {border} !important; border-radius: 4px; }}

/* Alerts / warnings */
div[data-testid="stAlert"] * {{
    color: {alert_body} !important;
}}

/* Primary download */
div[data-testid="stDownloadButton"] button {{
    min-height: 3.25rem !important;
    padding: 0 1.75rem !important;
    font-size: 1.05rem !important;
    font-weight: 600 !important;
}}
</style>
""",
        unsafe_allow_html=True,
    )


def render_site_nav() -> None:
    """Brand, theme toggle, and page links (theme preserved via URL + session)."""
    hydrate_theme_from_url()

    top = st.columns([4, 1])
    with top[0]:
        st.markdown(
            '<p class="portfolio-brand">JACK DRU<span>Y</span>ON</p>',
            unsafe_allow_html=True,
        )
    with top[1]:
        st.toggle(
            "Dark mode",
            key=THEME_SESSION,
            on_change=_push_theme_to_url,
        )

    hr_color = "#2E2E36" if is_dark() else "#D9D4CC"
    st.markdown(
        f'<hr style="border:none;border-top:1px solid {hr_color};margin:4px 0 16px 0">',
        unsafe_allow_html=True,
    )

    qp = theme_query_params()
    nav = st.columns([1, 1, 1, 1])
    with nav[0]:
        st.page_link("app.py", label="Home", query_params=qp)
    with nav[1]:
        st.page_link("pages/1_Resume.py", label="Resume", query_params=qp)
    with nav[2]:
        st.page_link("pages/2_Projects.py", label="Projects", query_params=qp)
    with nav[3]:
        st.page_link("pages/3_Contact.py", label="Contact", query_params=qp)


def render_portfolio_chrome(*, show_hero: bool = False) -> None:
    """Nav + theme toggle, global CSS, optional landing hero (home only)."""
    render_site_nav()
    render_portfolio_styles()
    if show_hero:
        render_home_hero()


def render_home_hero() -> None:
    st.markdown(
        """
<div class="portfolio-hero">
  <h1>Jack Druyon</h1>
  <div class="role">Finance · Analytics · AI Automation · Problem Solving · Communication</div>
  <p>
    I build systems that turn noisy data into decisions executives can act on.
    This site summarizes my background and selected work, including analytics application
    (<strong style="color: inherit;">Elias</strong>) that structures guest feedback for reporting and search for Disney Experiences. I plan to build more tools to solver business problems as I grow my skills.
  </p>
</div>
""",
        unsafe_allow_html=True,
    )
