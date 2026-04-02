#!/usr/bin/env python3
"""Streamlit Cloud 默认入口。

用于部署场景（如 Streamlit Community Cloud）中固定查找 `streamlit_app.py` 的约定。
"""

from web.app import main


if __name__ == "__main__":
    main()
