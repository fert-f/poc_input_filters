from __future__ import annotations

import sys
from pathlib import Path

import pandas as pd
import streamlit as st

ROOT = Path(__file__).resolve().parent
SRC = ROOT / "src"
sys.path.insert(0, str(SRC))

from poc_input_filters.filters import (  # noqa: E402
    CleanTextOptions,
    FilterOptions,
    analyze_text,
    apply_filters,
)
from poc_input_filters.highlight import (  # noqa: E402
    DEFAULT_GROUPS,
    highlight_css,
    render_highlight,
)
from poc_input_filters.presets import PRESETS  # noqa: E402

st.set_page_config(page_title="Input Filter POC", layout="wide")

st.title("Input Filter POC")
st.markdown(
    "Demonstrate how invisible or malformed characters can smuggle content into "
    "human-to-LLM messages, then apply filters to reduce risk.",
)

st.markdown(highlight_css(), unsafe_allow_html=True)

preset_labels = ["(Custom input)"] + [preset.label for preset in PRESETS]
default_label = "All groups showcase"
default_index = (
    preset_labels.index(default_label) if default_label in preset_labels else 0
)
selected_preset = st.sidebar.selectbox(
    "Preset samples",
    preset_labels,
    index=default_index,
)

if "input_text" not in st.session_state:
    st.session_state.input_text = ""

if selected_preset != "(Custom input)":
    chosen = next(p for p in PRESETS if p.label == selected_preset)
    st.session_state.input_text = chosen.text
    st.sidebar.caption(chosen.description)

raw_text = st.sidebar.text_area(
    "Message input",
    key="input_text",
    height=220,
    placeholder="Paste or type a message...",
)

st.sidebar.header("Filters")
use_ftfy = st.sidebar.checkbox("Fix encoding issues (ftfy)", value=True)
strip_invisible = st.sidebar.checkbox(
    "Strip control/format/invisible chars",
    value=True,
)
use_clean_text = st.sidebar.checkbox("Apply clean-text", value=False)

clean_options = CleanTextOptions()
if use_clean_text:
    st.sidebar.caption("clean-text toggles")
    clean_options = CleanTextOptions(
        fix_unicode=st.sidebar.checkbox("fix_unicode", value=True),
        to_ascii=st.sidebar.checkbox("to_ascii", value=False),
        no_urls=st.sidebar.checkbox("no_urls", value=False),
        no_emails=st.sidebar.checkbox("no_emails", value=False),
        no_phone_numbers=st.sidebar.checkbox("no_phone_numbers", value=False),
        no_numbers=st.sidebar.checkbox("no_numbers", value=False),
        no_digits=st.sidebar.checkbox("no_digits", value=False),
        no_currency_symbols=st.sidebar.checkbox("no_currency_symbols", value=False),
        no_punct=st.sidebar.checkbox("no_punct", value=False),
    )

st.sidebar.header("Custom regex")
regex_enabled = st.sidebar.checkbox("Enable regex filter", value=False)
regex_pattern = st.sidebar.text_input(
    "Pattern",
    value=r"[\u200B-\u200F]",
    help="Use Python regex syntax. Unicode ranges work in the regex module.",
)
regex_replacement = st.sidebar.text_input("Replacement", value="")
regex_timeout_ms = st.sidebar.slider("Regex timeout (ms)", 10, 500, 50)

filter_options = FilterOptions(
    use_ftfy=use_ftfy,
    strip_invisible=strip_invisible,
    use_clean_text=use_clean_text,
    regex_enabled=regex_enabled,
    regex_pattern=regex_pattern,
    regex_replacement=regex_replacement,
    regex_timeout_ms=regex_timeout_ms,
)

raw_findings = analyze_text(raw_text)
highlight_groups = DEFAULT_GROUPS

filter_result = apply_filters(raw_text, filter_options, clean_options)
filtered_text = filter_result.text
filtered_findings = analyze_text(filtered_text)

if filter_result.warnings:
    st.warning(" ".join(filter_result.warnings))

left, right = st.columns(2)
with left:
    st.subheader("Original")
    st.markdown(
        render_highlight(raw_text, raw_findings, highlight_groups),
        unsafe_allow_html=True,
    )

with right:
    st.subheader("Filtered")
    st.markdown(
        render_highlight(filtered_text, filtered_findings, highlight_groups),
        unsafe_allow_html=True,
    )

st.subheader("Findings table")
if raw_findings:
    table_data = [
        {
            "index": f.index,
            "group": f.group,
            "codepoint": f.codepoint,
            "name": f.name,
            "category": f.category,
            "char_repr": repr(f.char),
            "description": f.description,
        }
        for f in raw_findings
    ]
    st.dataframe(pd.DataFrame(table_data), use_container_width=True)
else:
    st.caption("No findings to show.")
