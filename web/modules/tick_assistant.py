"""A股/期货 Tick 交易助手模块（可嵌入主 Streamlit 应用）。"""

from __future__ import annotations

import datetime as dt
from typing import Callable, Tuple

import pandas as pd
import streamlit as st


DataFetcher = Callable[[str], pd.DataFrame]


def _safe_numeric(series: pd.Series) -> pd.Series:
    """将字符串价格/成交量列尽可能转换为数值。"""
    return pd.to_numeric(series.astype(str).str.replace(",", ""), errors="coerce")


def _normalize_tick_df(df: pd.DataFrame) -> pd.DataFrame:
    """统一字段命名，便于在前端展示。"""
    renamed = df.copy()
    mapping = {
        "time": "时间",
        "成交时间": "时间",
        "datetime": "时间",
        "price": "价格",
        "成交价": "价格",
        "close": "价格",
        "last": "价格",
        "volume": "成交量",
        "成交量": "成交量",
        "position": "持仓量",
        "hold": "持仓量",
        "ask": "卖一",
        "bid": "买一",
        "type": "方向",
        "性质": "方向",
    }
    renamed = renamed.rename(columns={k: v for k, v in mapping.items() if k in renamed.columns})

    if "价格" in renamed.columns:
        renamed["价格"] = _safe_numeric(renamed["价格"])
    if "成交量" in renamed.columns:
        renamed["成交量"] = _safe_numeric(renamed["成交量"])
    if "持仓量" in renamed.columns:
        renamed["持仓量"] = _safe_numeric(renamed["持仓量"])

    return renamed


def _fetch_a_share_tick(symbol: str, trade_date: dt.date) -> Tuple[pd.DataFrame, str]:
    import akshare as ak

    ymd = trade_date.strftime("%Y%m%d")
    fetchers: list[tuple[str, DataFetcher]] = [
        ("stock_zh_a_tick_tx_js", lambda s: ak.stock_zh_a_tick_tx_js(symbol=s)),
        ("stock_zh_a_tick_163", lambda s: ak.stock_zh_a_tick_163(symbol=s, date=ymd)),
        ("stock_intraday_em", lambda s: ak.stock_intraday_em(symbol=s)),
    ]

    errors = []
    for name, fetcher in fetchers:
        try:
            df = fetcher(symbol)
            if isinstance(df, pd.DataFrame) and not df.empty:
                return _normalize_tick_df(df), name
        except Exception as exc:  # noqa: BLE001
            errors.append(f"{name}: {exc}")

    raise RuntimeError("A股 tick 获取失败\n" + "\n".join(errors))


def _fetch_futures_tick(symbol: str) -> Tuple[pd.DataFrame, str]:
    import akshare as ak

    fetchers: list[tuple[str, DataFetcher]] = [
        ("futures_zh_realtime", lambda s: ak.futures_zh_realtime(symbol=s)),
        ("futures_zh_spot", lambda s: ak.futures_zh_spot(symbol=s, market="CF")),
        ("futures_zh_minute_sina(1m)", lambda s: ak.futures_zh_minute_sina(symbol=s, period="1")),
    ]

    errors = []
    for name, fetcher in fetchers:
        try:
            df = fetcher(symbol)
            if isinstance(df, pd.DataFrame) and not df.empty:
                return _normalize_tick_df(df), name
        except Exception as exc:  # noqa: BLE001
            errors.append(f"{name}: {exc}")

    raise RuntimeError("期货 tick 获取失败\n" + "\n".join(errors))


def _render_table_and_chart(df: pd.DataFrame) -> None:
    c1, c2, c3 = st.columns(3)
    c1.metric("记录数", f"{len(df):,}")
    if "价格" in df.columns and df["价格"].notna().any():
        c2.metric("最新价", f"{df['价格'].dropna().iloc[-1]:.4f}")
        c3.metric("均价", f"{df['价格'].dropna().mean():.4f}")

    st.dataframe(df, use_container_width=True, height=460)

    if "价格" in df.columns and df["价格"].notna().any():
        plot_df = df.reset_index(drop=True).copy()
        if "时间" in plot_df.columns:
            x_col = "时间"
        else:
            plot_df["序号"] = plot_df.index
            x_col = "序号"
        st.line_chart(plot_df.set_index(x_col)["价格"])


def render_tick_assistant() -> None:
    """渲染 Tick 交易助手（主应用内嵌页面）。"""
    st.header("📉 A股/期货 Tick 交易助手")
    st.caption("基于 AkShare 的 tick 级数据获取 + Streamlit 前端展示")

    market = st.radio("市场", ["A股", "期货"], horizontal=True)
    symbol = st.text_input(
        "代码",
        value="600519" if market == "A股" else "IF0",
        help="A股示例: 600519 / 000001；期货示例: IF0 / RB0 / AU0",
    ).strip()
    trade_date = st.date_input("交易日（A股接口可能会用到）", value=dt.date.today())

    st.info("提示：不同 AkShare 接口可用性会随交易时段/数据源状态变化。")

    if not st.button("获取 Tick 数据", type="primary", use_container_width=False):
        st.write("请输入代码并点击 **获取 Tick 数据**。")
        return

    if not symbol:
        st.error("请输入有效代码。")
        return

    with st.spinner("正在从 AkShare 拉取数据..."):
        try:
            if market == "A股":
                df, source = _fetch_a_share_tick(symbol, trade_date)
            else:
                df, source = _fetch_futures_tick(symbol)
        except Exception as exc:  # noqa: BLE001
            st.error(f"数据获取失败：{exc}")
            return

    st.success(f"数据获取成功，来源接口：`{source}`")
    _render_table_and_chart(df)

    csv_data = df.to_csv(index=False).encode("utf-8-sig")
    st.download_button(
        "下载 CSV",
        data=csv_data,
        file_name=f"{market}_{symbol}_tick_{dt.datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
        mime="text/csv",
    )
