#!/usr/bin/env python3
"""A股/期货 Tick 交易助手独立启动入口。"""

import streamlit as st

from modules.tick_assistant import render_tick_assistant


st.set_page_config(page_title="A股/期货 Tick 交易助手", page_icon="📉", layout="wide")


def main() -> None:
    st.title("📉 A股/期货 Tick 交易助手")
    render_tick_assistant()


if __name__ == "__main__":
    main()
