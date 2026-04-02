#!/usr/bin/env python3
"""Streamlit Cloud 默认入口。

用于部署场景（如 Streamlit Community Cloud）中固定查找 `streamlit_app.py` 的约定。
"""

from __future__ import annotations

from importlib.util import module_from_spec, spec_from_file_location
from pathlib import Path
import sys


ROOT_DIR = Path(__file__).resolve().parent
WEB_APP_PATH = ROOT_DIR / "web" / "app.py"


def _load_web_main():
    """从 web/app.py 显式加载 main，避免与根目录 app/ 包冲突。"""
    web_dir = str(WEB_APP_PATH.parent)
    if web_dir not in sys.path:
        sys.path.insert(0, web_dir)

    spec = spec_from_file_location("tradingagents_web_app", WEB_APP_PATH)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"无法加载 Streamlit 主程序: {WEB_APP_PATH}")

    module = module_from_spec(spec)
    spec.loader.exec_module(module)
    if not hasattr(module, "main"):
        raise RuntimeError("web/app.py 缺少 main() 入口")
    return module.main


if __name__ == "__main__":
    _load_web_main()()
