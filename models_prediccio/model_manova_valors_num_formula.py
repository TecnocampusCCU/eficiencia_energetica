import numpy as np
import pandas as pd
from sqlalchemy import create_engine
from sqlalchemy.engine import URL

from sklearn.linear_model import LinearRegression
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_absolute_error, mean_squared_error

try:
    from sklearn.metrics import root_mean_squared_error
    HAVE_RMSE = True
except Exception:
    HAVE_RMSE = False

# --- Conexión (ajusta password)
db_url = URL.create(
    drivername="postgresql+psycopg2",
    username="ccu",
    password="Cu25Cc14",
    host="172.20.250.8",
    port=5432,
    database="ccu_db_new",
)
engine = create_engine(db_url)

# --- TRAIN: 1 fila por edificio (14 dígitos) + nº viviendas (habitatges)
train_sql = """
WITH census_counts AS (
    SELECT
        c.cadastral_reference,
        COUNT(*)::int AS n_residents
    FROM census c
    GROUP BY c.cadastral_reference
),
hab_counts AS (
    SELECT
        h.parcela_catastral AS cadastral_reference,
        COUNT(*)::int AS n_habitatges
    FROM habitatges_mataro_cat h
    GROUP BY h.parcela_catastral
),
cert_agg AS (
    SELECT
        LEFT(c."referencia cadastral", 14) AS cadastral_reference_14,
        SUM(c."energia primària no renovable"::double precision) AS energia_sum,
        SUM(c."emissions de co2"::double precision) AS co2_sum
    FROM cert_efi_energ_edif_mataro_geom c
    WHERE c."energia primària no renovable" IS NOT NULL
      AND c."emissions de co2" IS NOT NULL
    GROUP BY LEFT(c."referencia cadastral", 14)
)
SELECT
    b.id_building,
    b.cadastral_reference AS cadastral_reference,
    b.area_value AS m2,
    (EXTRACT(YEAR FROM CURRENT_DATE) - EXTRACT(YEAR FROM b.date_of_construction))::int AS antiguitat,
    COALESCE(cc.n_residents, 0) AS n_residents,
    COALESCE(hc.n_habitatges, 0) AS n_habitatges,
    ca.energia_sum AS energia,
    ca.co2_sum AS co2
FROM building b
JOIN cert_agg ca
    ON ca.cadastral_reference_14 = b.cadastral_reference
LEFT JOIN census_counts cc
    ON b.cadastral_reference = cc.cadastral_reference
LEFT JOIN hab_counts hc
    ON b.cadastral_reference = hc.cadastral_reference
WHERE b.area_value IS NOT NULL
  AND b.date_of_construction IS NOT NULL
  AND b.current_use = '1_residential'
"""

# --- PRED: edificios residenciales sin certificados + nº viviendas
pred_sql = """
WITH census_counts AS (
    SELECT
        c.cadastral_reference,
        COUNT(*)::int AS n_residents
    FROM census c
    GROUP BY c.cadastral_reference
),
hab_counts AS (
    SELECT
        h.parcela_catastral AS cadastral_reference,
        COUNT(*)::int AS n_habitatges
    FROM habitatges_mataro_cat h
    GROUP BY h.parcela_catastral
),
cert_buildings AS (
    SELECT DISTINCT
        LEFT(c."referencia cadastral", 14) AS cadastral_reference_14
    FROM cert_efi_energ_edif_mataro_geom c
)
SELECT
    b.id_building,
    b.cadastral_reference,
    b.area_value AS m2,
    (EXTRACT(YEAR FROM CURRENT_DATE) - EXTRACT(YEAR FROM b.date_of_construction))::int AS antiguitat,
    COALESCE(cc.n_residents, 0) AS n_residents,
    COALESCE(hc.n_habitatges, 0) AS n_habitatges
FROM building b
LEFT JOIN cert_buildings cb
    ON cb.cadastral_reference_14 = b.cadastral_reference
LEFT JOIN census_counts cc
    ON b.cadastral_reference = cc.cadastral_reference
LEFT JOIN hab_counts hc
    ON b.cadastral_reference = hc.cadastral_reference
WHERE cb.cadastral_reference_14 IS NULL
  AND b.area_value IS NOT NULL
  AND b.date_of_construction IS NOT NULL
  AND b.current_use = '1_residential'
"""

# --- Cargar datos
df_train = pd.read_sql(train_sql, engine)
df_pred  = pd.read_sql(pred_sql, engine)

# (Extra) por seguridad: asegurar 1 fila por referencia (sum targets, max antiguitat)
df_train = (
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

# --- Features (ahora incluye n_habitatges)
X = df_train[["antiguitat", "m2", "n_residents", "n_habitatges"]].to_numpy(dtype=float)
Y = df_train[["energia", "co2"]].to_numpy(dtype=float)

X_pred = df_pred[["antiguitat", "m2", "n_residents", "n_habitatges"]].to_numpy(dtype=float)

# --- Split
X_tr, X_te, Y_tr, Y_te = train_test_split(X, Y, test_size=0.2, random_state=0)

# --- Modelo lineal multioutput
lr = LinearRegression()
lr.fit(X_tr, Y_tr)

# --- Evaluación
Yhat_te = lr.predict(X_te)
mae = mean_absolute_error(Y_te, Yhat_te, multioutput="raw_values")

if HAVE_RMSE:
    rmse = root_mean_squared_error(Y_te, Yhat_te, multioutput="raw_values")
else:
    mse = mean_squared_error(Y_te, Yhat_te, multioutput="raw_values")
    rmse = np.sqrt(mse)

print(f"[Energia (sum)] MAE={mae[0]:.4f} RMSE={rmse[0]:.4f}")
print(f"[CO2 (sum)]     MAE={mae[1]:.4f} RMSE={rmse[1]:.4f}")

# --- Fórmulas
feature_names = ["antiguitat", "m2", "n_residents", "n_habitatges"]

b0_E, b0_C = lr.intercept_[0], lr.intercept_[1]
coef_E, coef_C = lr.coef_[0], lr.coef_[1]

print("\nFormula energia (sum por edificio):")
print(
    "energia = {:.6f} + ({:.6f})*antiguitat + ({:.6f})*m2 + ({:.6f})*n_residents + ({:.6f})*n_habitatges".format(
        b0_E, coef_E[0], coef_E[1], coef_E[2], coef_E[3]
    )
)

print("\nFormula CO2 (sum por edificio):")
print(
    "co2 = {:.6f} + ({:.6f})*antiguitat + ({:.6f})*m2 + ({:.6f})*n_residents + ({:.6f})*n_habitatges".format(
        b0_C, coef_C[0], coef_C[1], coef_C[2], coef_C[3]
    )
)

# --- Predicción edificios sin certificados
Yhat_pred = lr.predict(X_pred)
df_pred["pred_energia_sum"] = Yhat_pred[:, 0]
df_pred["pred_co2_sum"]     = Yhat_pred[:, 1]

print("\nPredicciones (primeras filas):")
print(df_pred[["id_building", "cadastral_reference", "pred_energia_sum", "pred_co2_sum"]].head())

# --- (Opcional) Guardar a tabla
# df_pred[["id_building", "cadastral_reference", "pred_energia_sum", "pred_co2_sum"]].to_sql(
#     "prediccions_valors_consum_i_co2_lr_building_sum_vivendes",
#     engine,
#     if_exists="replace",
#     index=False
# )
