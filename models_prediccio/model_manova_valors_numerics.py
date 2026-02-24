import numpy as np
import pandas as pd

from sklearn.linear_model import LinearRegression
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_absolute_error, mean_squared_error

try:
    from sklearn.metrics import root_mean_squared_error
    HAVE_RMSE = True
except Exception:
    HAVE_RMSE = False


TRAIN_SQL = """... TU train_sql EXACTO ..."""
PRED_SQL  = """... TU pred_sql EXACTO ..."""

FEATURES = ["antiguitat", "m2", "n_residents", "n_habitatges"]


def _read_df_psycopg2(conn, sql: str) -> pd.DataFrame:
    # conn: psycopg2.connection
    with conn.cursor() as cur:
        cur.execute(sql)
        rows = cur.fetchall()
        cols = [d.name for d in cur.description]
    return pd.DataFrame(rows, columns=cols)


def load_data(conn):
    df_train = _read_df_psycopg2(conn, TRAIN_SQL)
    df_pred  = _read_df_psycopg2(conn, PRED_SQL)
    return df_train, df_pred


def aggregate_train(df_train: pd.DataFrame) -> pd.DataFrame:
    return (
        df_train.groupby("cadastral_reference", as_index=False)
        .agg(
            id_building=("id_building", "min"),
            m2=("m2", "max"),
            antiguitat=("antiguitat", "max"),
            n_residents=("n_residents", "max"),
            n_habitatges=("n_habitatges", "max"),
            energia=("energia", "sum"),
            co2=("co2", "sum"),
        )
    )


def fit_model(df_train_agg: pd.DataFrame):
    X = df_train_agg[FEATURES].to_numpy(dtype=float)
    Y = df_train_agg[["energia", "co2"]].to_numpy(dtype=float)

    X_tr, X_te, Y_tr, Y_te = train_test_split(X, Y, test_size=0.2, random_state=0)

    lr = LinearRegression()
    lr.fit(X_tr, Y_tr)

    Yhat_te = lr.predict(X_te)
    mae = mean_absolute_error(Y_te, Yhat_te, multioutput="raw_values")

    if HAVE_RMSE:
        rmse = root_mean_squared_error(Y_te, Yhat_te, multioutput="raw_values")
    else:
        mse = mean_squared_error(Y_te, Yhat_te, multioutput="raw_values")
        rmse = np.sqrt(mse)

    metrics = {
        "mae_energia": float(mae[0]),
        "rmse_energia": float(rmse[0]),
        "mae_co2": float(mae[1]),
        "rmse_co2": float(rmse[1]),
    }
    return lr, metrics


def predict_missing(lr: LinearRegression, df_pred: pd.DataFrame) -> pd.DataFrame:
    X_pred = df_pred[FEATURES].to_numpy(dtype=float)
    Yhat_pred = lr.predict(X_pred)

    out = df_pred.copy()
    out["pred_energia_sum"] = Yhat_pred[:, 0]
    out["pred_co2_sum"] = Yhat_pred[:, 1]
    return out


def qgis_formulas(lr: LinearRegression, field_map=None, decimals: int = 6) -> dict:
    # En multioutput: coef_ tiene forma (n_targets, n_features). [web:16]
    if field_map is None:
        field_map = {
            "antiguitat": "antiguitat",
            "m2": "m2",
            "n_residents": "n_residents",
            "n_habitatges": "n_habitatges",
        }

    b0_E, b0_C = lr.intercept_[0], lr.intercept_[1]
    coef_E, coef_C = lr.coef_[0], lr.coef_[1]

    f_ant = f"\"{field_map['antiguitat']}\""
    f_m2  = f"\"{field_map['m2']}\""
    f_res = f"\"{field_map['n_residents']}\""
    f_hab = f"\"{field_map['n_habitatges']}\""

    fmt = f"{{:.{decimals}f}}"
    energia = (
        f"{fmt.format(b0_E)}"
        f" + ({fmt.format(coef_E[0])})*{f_ant}"
        f" + ({fmt.format(coef_E[1])})*{f_m2}"
        f" + ({fmt.format(coef_E[2])})*{f_res}"
        f" + ({fmt.format(coef_E[3])})*{f_hab}"
    )
    co2 = (
        f"{fmt.format(b0_C)}"
        f" + ({fmt.format(coef_C[0])})*{f_ant}"
        f" + ({fmt.format(coef_C[1])})*{f_m2}"
        f" + ({fmt.format(coef_C[2])})*{f_res}"
        f" + ({fmt.format(coef_C[3])})*{f_hab}"
    )

    return {"energia_qgis": energia, "co2_qgis": co2}


def run(conn):
    df_train, df_pred = load_data(conn)
    df_train_agg = aggregate_train(df_train)

    lr, metrics = fit_model(df_train_agg)
    formulas = qgis_formulas(lr)

    df_pred_out = predict_missing(lr, df_pred)
    return lr, metrics, formulas, df_pred_out

def build_qgis_formulas(conn, field_map=None, decimals: int = 6):
    df_train, _ = load_data(conn)
    df_train_agg = aggregate_train(df_train)
    lr, _metrics = fit_model(df_train_agg)
    f = qgis_formulas(lr, field_map=field_map, decimals=decimals)
    return f["energia_qgis"], f["co2_qgis"]