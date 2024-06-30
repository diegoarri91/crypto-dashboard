import datetime as dt
import requests
import toolz as fp

from binance.client import Client
import pandas as pd


BINANCE_KLINES_COLS = [
    "time_open",
    "price_open",
    "price_high",
    "price_low",
    "price_close",
    "volume",
    "time_close",
    "quote_asset_volume",
    "number_of_trades",
    "taker_buy_base_asset_volume",
    "taker_buy_quote_asset_volume",
    "ignore"
]
SCHEMA = {
    "price_open": float,
    "price_high": float,
    "price_low": float,
    "price_close": float,
}
BINANCE2PANDAS_INTERVAL_STR = {
    "1m": "1min",
    "1h": "1h"
}
TIMEDATE_STRING_FORMAT = "%Y-%m-%dT%H:%M"


def minute_rounding(datetime, rounding_minutes: int = 15):
    return dt.datetime(datetime.year, datetime.month, datetime.day,
                       datetime.hour, datetime.minute // rounding_minutes * rounding_minutes)


@fp.curry
def set_time_index(
    df: pd.DataFrame,
    column: str,
    freq: str = "1min"
):
    """

    Args:
        df (pd.DataFrame): Input dataframe.
        column (str): Timedate column.
        freq (str): "min", "1min", "5min", "10min", "h", "2h".
    """
    minutes = pd.Index(pd.date_range(
        start=df[column].min().strftime("%Y-%m-%dT%H:%M"),
        end=df[column].max().strftime("%Y-%m-%dT%H:%M"),
        freq=freq,
        tz="utc"
    ), name=column)
    return df.set_index(column).reindex(index=minutes).reset_index(level=column)


@fp.curry
def preprocessing(
    df: pd.DataFrame,
    time_column: str = "timestamp",
    freq: str = "1min"
):
    """
    General preprocessing of the data.

    Args:
        df (pd.DataFrame): Input dataframe.
        time_column (str): Column used to define time index. Handles Unix epochs.
        freq (str): "min", "1min", "5min", "10min", "h", "2h"
    """
    return (
        df
        .assign(**{time_column: pd.to_datetime(df["time_open"], unit='ms', utc=True)})
        .pipe(set_time_index(column=time_column, freq=freq))
    )


def get_last_historical_klines(
    start,
    end,
    symbol: str = "BTCUSDT",
    interval: str = "1m",
    api_key: str = None,
    api_secret: str = None
):
    client = Client(api_key, api_secret)
    return (
        pd.DataFrame(client.get_historical_klines(
            symbol,
            interval,
            start.strftime(TIMEDATE_STRING_FORMAT),
            end.strftime(TIMEDATE_STRING_FORMAT)), columns=BINANCE_KLINES_COLS)
        .pipe(preprocessing(time_column="timestamp", freq=BINANCE2PANDAS_INTERVAL_STR[interval]))
        .astype(SCHEMA)
    )


def get_prediction(input_df, mock: bool = False):
    if not mock:
        response = requests.post(url='http://127.0.0.1:8000/predict', json=input_df[["price_high", "price_low", "price_close"]].to_dict(orient="list"))
        return pd.DataFrame(response.json()["prediction"])
    else:
        return pd.DataFrame({
            "6h": {"prediction": 60e3, "prediction_normalized": -1e-3, "prediction_binary": 0.46},
            "12h": {"prediction": 62e3, "prediction_normalized": 1e-3, "prediction_binary": 0.8}
        })
