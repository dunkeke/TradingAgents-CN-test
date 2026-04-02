#!/usr/bin/env python3
"""Streamlit Cloud 默认入口。

用于部署场景（如 Streamlit Community Cloud）中固定查找 `streamlit_app.py` 的约定。
"""

from pathlib import Path
import sys

# 确保可导入 web/ 目录下的 app.py 与其同级组件模块（components/, modules/, utils/）
ROOT_DIR = Path(__file__).resolve().parent
WEB_DIR = ROOT_DIR / "web"
if str(WEB_DIR) not in sys.path:
    sys.path.insert(0, str(WEB_DIR))

from app import main  # noqa: E402


if __name__ == "__main__":
    main()
