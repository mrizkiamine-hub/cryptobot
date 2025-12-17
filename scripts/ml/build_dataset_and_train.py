import json
from dataclasses import dataclass
from datetime import datetime
import pandas as pd
import psycopg2

from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler
from sklearn.linear_model import Ridge
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score

PG_CONFIG = {
    "host": "localhost",
    "port": 5432,
    "dbname": "dst_db",
    "user": "daniel",
    "password": "datascientest",
}


@dataclass
class MLConfig:
    market_symbol: str = "BTCUSDT"
    interval_code: str = "1h"
    horizon: int = 1          # target = return future à H pas (1h ou 4h)
    split_ratio: float = 0.8  # split temporel
    ma_windows: tuple[int, int] = (10, 20)
    vol_window: int = 20


def read_market_from_db(cfg: MLConfig) -> pd.DataFrame:
    query = """
        SELECT
            f.open_time,
            f.close,
            f.volume_base
        FROM cryptobot.fact_market_price f
        JOIN cryptobot.dim_market m ON m.id = f.market_id
        WHERE m.symbol = %s
          AND f.interval_code = %s
        ORDER BY f.open_time ASC
    """

    with psycopg2.connect(**PG_CONFIG) as conn:
        df = pd.read_sql(query, conn, params=(cfg.market_symbol, cfg.interval_code))

    df["open_time"] = pd.to_datetime(df["open_time"], utc=True)
    df = df.drop_duplicates(subset=["open_time"]).set_index("open_time").sort_index()
    return df


def build_features(df: pd.DataFrame, cfg: MLConfig) -> pd.DataFrame:
    out = df.copy()

    # returns (pas de fuite: uniquement passé)
    out["return_1"] = out["close"].pct_change(1)
    out["log_return_1"] = (out["close"].apply(lambda x: None if x <= 0 else x)).astype(float)
    out["log_return_1"] = pd.Series(pd.NA, index=out.index).where(out["close"] <= 0, out["close"]).astype(float)
    out["log_return_1"] = (pd.Series(pd.NA, index=out.index)
                           .where(out["close"] <= 0, out["close"])
                           .astype(float))
    # version simple / robuste:
    out["log_return_1"] = (pd.Series(out["close"]).apply(lambda x: pd.NA if x <= 0 else x)).astype("float64")
    out["log_return_1"] = pd.Series(pd.NA, index=out.index).astype("float64")
    out.loc[out["close"] > 0, "log_return_1"] = pd.np.log(out.loc[out["close"] > 0, "close"])  # compat DST simple
    out["log_return_1"] = out["log_return_1"].diff(1)

    w1, w2 = cfg.ma_windows
    out[f"ma_{w1}"] = out["close"].rolling(w1).mean()
    out[f"ma_{w2}"] = out["close"].rolling(w2).mean()

    out[f"vol_{cfg.vol_window}"] = out["return_1"].rolling(cfg.vol_window).std()

    # volumes (souvent utile)
    out["vol_chg_1"] = out["volume_base"].pct_change(1)
    out[f"vol_ma_{w1}"] = out["volume_base"].rolling(w1).mean()

    # target (futur) : return à horizon H
    out[f"target_return_h{cfg.horizon}"] = out["close"].shift(-cfg.horizon) / out["close"] - 1

    # nettoyage (drop NA dus aux rolling + target shift)
    out = out.dropna()

    return out


def time_split(df_feat: pd.DataFrame, cfg: MLConfig):
    cut = int(len(df_feat) * cfg.split_ratio)
    train = df_feat.iloc[:cut]
    test = df_feat.iloc[cut:]

    y_col = f"target_return_h{cfg.horizon}"
    X_cols = [c for c in df_feat.columns if c != y_col]

    X_train, y_train = train[X_cols], train[y_col]
    X_test, y_test = test[X_cols], test[y_col]
    return X_train, X_test, y_train, y_test


def train_baseline(X_train, y_train):
    pipe = Pipeline([
        ("scaler", StandardScaler()),
        ("model", Ridge(alpha=1.0)),
    ])
    pipe.fit(X_train, y_train)
    return pipe


def evaluate(model, X_test, y_test) -> dict:
    pred = model.predict(X_test)
    return {
        "mae": float(mean_absolute_error(y_test, pred)),
        "rmse": float(mean_squared_error(y_test, pred) ** 0.5),
        "r2": float(r2_score(y_test, pred)),
        "n_test": int(len(y_test)),
    }


if __name__ == "__main__":
    cfg = MLConfig(market_symbol="BTCUSDT", interval_code="1h", horizon=1)

    df = read_market_from_db(cfg)
    df_feat = build_features(df, cfg)

    X_train, X_test, y_train, y_test = time_split(df_feat, cfg)

    model = train_baseline(X_train, y_train)
    metrics = evaluate(model, X_test, y_test)

    print("[METRICS]", json.dumps(metrics, indent=2))
