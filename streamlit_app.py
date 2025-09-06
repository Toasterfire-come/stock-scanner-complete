from __future__ import annotations

from typing import List

import pandas as pd
import plotly.express as px
import streamlit as st

from trends_tool.core import TrendsConfig, fetch_interest_over_time, fetch_related_queries


def _parse_keywords(text: str) -> List[str]:
    return [token.strip() for token in text.split(",") if token.strip()]


st.set_page_config(page_title="Scanner Trends Gauge", page_icon="📈", layout="wide")
st.title("Gauge searches for scanner keywords")
st.caption("Compare Google Trends for 'stock scanner', 'market scanner', and 'trade scanner'.")

with st.sidebar:
    st.header("Parameters")
    keywords_text = st.text_input(
        "Keywords (comma-separated)",
        value="stock scanner, market scanner, trade scanner",
    )
    timeframe_label = st.selectbox(
        "Timeframe",
        index=1,
        options=[
            ("Past 30 days", "today 1-m"),
            ("Past 12 months", "today 12-m"),
            ("Past 5 years", "today 5-y"),
            ("2004-present", "all"),
        ],
        format_func=lambda x: x[0],
    )
    geo = st.selectbox(
        "Region",
        options=["Worldwide", "US", "GB", "IN", "CA", "AU"],
        index=0,
    )
    gprop = st.selectbox(
        "Property",
        options=[("Web Search", ""), ("Image", "images"), ("News", "news"), ("YouTube", "youtube"), ("Shopping", "froogle")],
        index=0,
        format_func=lambda x: x[0],
    )
    show_related = st.checkbox("Show related queries", value=False)

keywords = _parse_keywords(keywords_text)
timeframe = timeframe_label[1]
geo_code = "" if geo == "Worldwide" else geo
gprop_code = gprop[1]

config = TrendsConfig(
    keywords=keywords,
    timeframe=timeframe,
    geo=geo_code,
    gprop=gprop_code,
)

try:
    interest_df = fetch_interest_over_time(config)
except RuntimeError as dependency_error:
    st.error(str(dependency_error))
    st.stop()

if interest_df.empty:
    st.info("No data returned for the current parameters.")
    st.stop()

st.subheader("Interest over time (0-100)")
interest_reset = interest_df.reset_index().rename(columns={"date": "Date"})
fig = px.line(interest_reset, x="Date", y=interest_df.columns, title="Google Trends interest")
fig.update_layout(legend_title_text="Keyword")
st.plotly_chart(fig, use_container_width=True)

csv_bytes = interest_df.to_csv().encode("utf-8")
st.download_button("Download CSV", data=csv_bytes, file_name="scanner_trends.csv", mime="text/csv")

if show_related:
    st.subheader("Related queries")
    related = fetch_related_queries(config)
    for keyword, sections in related.items():
        with st.expander(f"{keyword}"):
            for section_name in ("top", "rising"):
                st.markdown(f"**{section_name.title()}**")
                df = sections.get(section_name)
                if df is None or df.empty:
                    st.write("(none)")
                else:
                    st.dataframe(df.head(20), use_container_width=True)

