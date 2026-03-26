import os
from datetime import datetime, timedelta, date
from email.mime.text import MIMEText
import smtplib

import pandas as pd
from dotenv import load_dotenv
from supabase import create_client


load_dotenv()

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

supabase = create_client(SUPABASE_URL, SUPABASE_KEY)


def load_all_insights(page_size: int = 1000) -> pd.DataFrame:
    all_rows = []
    page = 0
    while True:
        start = page * page_size
        end = start + page_size - 1
        result = (
            supabase.table("insights")
            .select("*")
            .order("weighted_score", desc=True)
            .range(start, end)
            .execute()
        )
        data = result.data or []
        if not data:
            break
        all_rows.extend(data)
        if len(data) < page_size:
            break
        page += 1

    if not all_rows:
        return pd.DataFrame()

    df = pd.DataFrame(all_rows)
    for col in ["date_added", "date_posted"]:
        if col in df.columns:
            df[col] = pd.to_datetime(df[col], errors="coerce", utc=True)
    return df


def get_week_options_from_df(df: pd.DataFrame):
    if df.empty:
        return []
    date_col = None
    for c in ["date_added", "date_posted"]:
        if c in df.columns and df[c].notna().any():
            date_col = c
            break
    if not date_col:
        return []
    dates = df[date_col].dropna()
    if dates.empty:
        return []
    latest = dates.max().date()
    earliest = dates.min().date()
    week_start = latest - timedelta(days=latest.weekday())
    week_end = week_start + timedelta(days=6)
    weeks = []
    while week_end >= earliest:
        label = f"{week_start.strftime('%b %d, %Y')} – {week_end.strftime('%b %d, %Y')}"
        weeks.append((label, week_start, week_end))
        week_start -= timedelta(weeks=1)
        week_end -= timedelta(weeks=1)
    return weeks


def build_week_slice(df: pd.DataFrame):
    weeks = get_week_options_from_df(df)
    if not weeks:
        return pd.DataFrame(), "No Data"
    label, start, end = weeks[0]
    week_start = pd.Timestamp(start, tz="UTC")
    week_end = pd.Timestamp(end, tz="UTC") + pd.Timedelta(hours=23, minutes=59)
    date_col = None
    for c in ["date_added", "date_posted"]:
        if c in df.columns and df[c].notna().any():
            date_col = c
            break
    if date_col:
        week_df = df[(df[date_col] >= week_start) & (df[date_col] <= week_end)].copy()
    else:
        week_df = df.copy()
    return week_df, label


def build_email_body(week_df: pd.DataFrame, week_label: str, url: str) -> str:
    if week_df.empty:
        return f"Elias Weekly Report — {week_label}\n\nNo insights surfaced for this period.\n\nView dashboard: {url}"

    total = len(week_df)
    top_cats = (
        week_df["category_tag"].value_counts().head(3).index.tolist()
        if "category_tag" in week_df.columns
        else []
    )

    proj_count = {}
    if "project_tags" in week_df.columns:
        all_tags = []
        for val in week_df["project_tags"].dropna():
            if isinstance(val, list):
                all_tags.extend(val)
            elif isinstance(val, str):
                all_tags.extend(
                    [p.strip().strip('"') for p in val.strip("{}").split(",") if p.strip()]
                )
        if all_tags:
            proj_count = {p: all_tags.count(p) for p in set(all_tags)}

    top3 = week_df.sort_values("upvotes", ascending=False).head(3)
    lines = []
    for _, r in top3.iterrows():
        rec = str(r.get("recommendation", "") or "").strip()
        upv = int(r.get("upvotes", 0) or 0)
        cat = str(r.get("category_tag", "")).replace("_", " ").title()
        proj = ""
        raw_p = r.get("project_tags")
        if raw_p:
            if isinstance(raw_p, list) and raw_p:
                proj = raw_p[0]
            elif isinstance(raw_p, str):
                proj = raw_p.strip("{}").split(",")[0].strip().strip('"')
        lines.append(f"  - {rec} — {cat} / {proj or 'General'} · ▲ {upv:,}")

    top_areas = sorted(proj_count, key=proj_count.get, reverse=True)[:4] if proj_count else []
    areas_str = ", ".join(top_areas) if top_areas else "General Disney"
    cat_str = ", ".join([c.replace("_", " ").title() for c in top_cats]) or "—"

    body = []
    body.append(f"ELIAS WEEKLY REPORT — {week_label}")
    body.append("=" * 50)
    body.append("")
    body.append(f"{total} insight{'s' if total != 1 else ''} surfaced this week.")
    body.append(f"Dominant categories: {cat_str}")
    body.append(f"Most-discussed areas: {areas_str}")
    body.append("")
    body.append("TOP 3 BY COMMUNITY VALIDATION")
    body.append("-" * 30)
    body.extend(lines)
    body.append("")
    body.append(f"View full dashboard: {url}")

    return "\n".join(body)


def send_email(subject: str, body: str):
    sender = os.getenv("REPORT_FROM")
    recipient = os.getenv("REPORT_TO")
    app_password = os.getenv("REPORT_APP_PASSWORD")

    if not sender or not recipient or not app_password:
        raise RuntimeError(
            "Missing REPORT_FROM, REPORT_TO, or REPORT_APP_PASSWORD in environment."
        )

    msg = MIMEText(body, "plain", "utf-8")
    msg["From"] = sender
    msg["To"] = recipient
    msg["Subject"] = subject

    with smtplib.SMTP_SSL("smtp.gmail.com", 465) as smtp:
        smtp.login(sender, app_password)
        smtp.send_message(msg)
    print(f"Email sent to {recipient}")


def main():
    url = "https://disneytool-production.up.railway.app"
    df = load_all_insights()
    week_df, week_label = build_week_slice(df)
    body = build_email_body(week_df, week_label, url)
    subject = f"Elias Weekly Report — {week_label}"
    send_email(subject, body)


if __name__ == "__main__":
    main()