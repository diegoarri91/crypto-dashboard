import datetime as dt

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st
from streamlit_autorefresh import st_autorefresh

from acquire import (
    BINANCE_KLINES_COLS, get_last_historical_klines, minute_rounding, preprocessing, SCHEMA,
    get_prediction
)


REFRESH_RATE = 3
MOCK = True
count = st_autorefresh(interval=60 * 1000, limit=None, key="autorefresh")


def get_last_historical_klines_with_mock(
    start,
    end,
):
    if not MOCK:
        return get_last_historical_klines(start, end)
    else:
        if "mock_df" not in st.session_state:
            st.session_state.mock_df = (
                pd.read_csv(f"/Users/diego.arribas/data/crypto-prediction/datasets/data_btc_usdt_2024_06_27.csv", header=0, names=BINANCE_KLINES_COLS)
                .pipe(preprocessing(time_column="timestamp", freq="1min"))
                .astype(SCHEMA)
            )
            st.session_state.counter = int(1e6)
        _df = st.session_state.mock_df.iloc[st.session_state.counter:st.session_state.counter + REFRESH_RATE]
        st.session_state.counter += REFRESH_RATE
        return _df


st.title("Dashboard")

placeholder = st.empty()

now = minute_rounding(dt.datetime.now(dt.timezone.utc), rounding_minutes=1)
rounded_now = minute_rounding(now, rounding_minutes=REFRESH_RATE)

if "df" not in st.session_state:
    st.session_state.df = get_last_historical_klines_with_mock(
        start=rounded_now - dt.timedelta(minutes=REFRESH_RATE),
        end=rounded_now - dt.timedelta(minutes=1)
    )
    get_prediction(input_df, mock=MOCK)
    st.session_state.next_update = rounded_now + dt.timedelta(minutes=REFRESH_RATE)


if now >= st.session_state.next_update:
    _df = get_last_historical_klines_with_mock(
        st.session_state.next_update - dt.timedelta(minutes=REFRESH_RATE),
        st.session_state.next_update - dt.timedelta(minutes=1)
    )
    st.session_state.df = pd.concat((st.session_state.df, _df), axis=0, ignore_index=True)
    st.session_state.next_update = rounded_now + dt.timedelta(minutes=REFRESH_RATE)


with placeholder.container():
    fig = go.Figure(
        data=[go.Candlestick(
            x=st.session_state.df['timestamp'],
            open=st.session_state.df['price_open'],
            high=st.session_state.df['price_high'],
            low=st.session_state.df['price_low'],
            close=st.session_state.df['price_close']
        )]
    )
    fig.update_layout(xaxis_rangeslider_visible=False)
    # fig = px.line(
    #     data_frame=st.session_state.df, x="timestamp", y="price_open"
    # )
    st.plotly_chart(fig)
