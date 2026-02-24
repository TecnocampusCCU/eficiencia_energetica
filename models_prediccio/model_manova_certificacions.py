import numpy as np
import pandas as pd

from sklearn.tree import DecisionTreeClassifier, export_text
from sklearn.utils.class_weight import compute_class_weight


def decision_tree_to_qgis_case(clf, feature_names, quote_fields=True):
    t = clf.tree_
    classes_ = list(getattr(clf, "classes_", []))

    def col(name: str) -> str:
        return f"\"{name}\"" if quote_fields else name

    def leaf_expr(node_id: int) -> str:
        counts = t.value[node_id][0]
        best_idx = int(np.argmax(counts))
        pred = classes_[best_idx] if classes_ else best_idx
        return f"'{pred}'" if isinstance(pred, str) else str(pred)

    def node_expr(node_id: int) -> str:
        feature_id = int(t.feature[node_id])
        if feature_id == -2:  # hoja
            return leaf_expr(node_id)

        name = feature_names[feature_id]
        thr = float(t.threshold[node_id])

        left_id = int(t.children_left[node_id])
        right_id = int(t.children_right[node_id])

        return (
            "(CASE "
            f"WHEN {col(name)} <= {repr(thr)} THEN {node_expr(left_id)} "
            f"ELSE {node_expr(right_id)} "
            "END)"
        )

    return node_expr(0)


def _fit_tree_and_case(df_train, feature_names, target_col, print_human_rules=False):
    df = df_train.loc[df_train[target_col].notna(), feature_names + [target_col]].copy()
    if df.empty:
        raise ValueError(f"No hay datos para entrenar el target '{target_col}' (todo es NULL).")

    X_train = df[feature_names].values
    y_train = df[target_col].values

    classes = np.unique(y_train)
    w_bal = compute_class_weight(class_weight="balanced", classes=classes, y=y_train)
    w_bal = dict(zip(classes, w_bal))

    alpha = 0.5
    w_smooth = {c: alpha * w + (1 - alpha) * 1.0 for c, w in w_bal.items()}

    # Mantengo tu ajuste específico si existe la clase 'E' en ese target
    if "E" in w_smooth:
        w_smooth["E"] = max(w_smooth.get("E", 1.0), 0.7)

    tree = DecisionTreeClassifier(
        criterion="gini",
        max_depth=5,
        min_samples_leaf=25,
        class_weight=w_smooth,
        random_state=0
    )
    tree.fit(X_train, y_train)

    if print_human_rules:
        rules = export_text(
            tree,
            feature_names=feature_names,
            class_names=list(tree.classes_),
            max_depth=10
        )
        print(f"\nRegles (humà) per target {target_col}:\n")
        print(rules)

    qgis_case = decision_tree_to_qgis_case(tree, feature_names=feature_names, quote_fields=True)
    return qgis_case


def generate_qgis_cases(conn, print_human_rules=False, print_qgis_case=True):
    # Feature set (m2 -> metres_cadastre)
    feature_names = ["antiguitat", "metres_cadastre", "n_residents"]

    train_sql = """
    WITH census_counts AS (
        SELECT
            c.cadastral_reference,
            COUNT(*)::int AS n_residents
        FROM census c
        GROUP BY c.cadastral_reference
    )
    SELECT
        c.id,
        b.area_value AS metres_cadastre,
        (EXTRACT(YEAR FROM CURRENT_DATE) - EXTRACT(YEAR FROM b.date_of_construction))::int AS antiguitat,
        COALESCE(cc.n_residents, 0) AS n_residents,
        c."qualificació de consum energia primaria no renovable" AS qual_consum,
        c."qualificacio emissions de co2" AS qual_emissions
    FROM cert_efi_energ_edif_mataro_geom c
    JOIN building b
        ON LEFT(c."referencia cadastral", 14) = b.cadastral_reference
    LEFT JOIN census_counts cc
        ON b.cadastral_reference = cc.cadastral_reference
    WHERE c.m2real IS NOT NULL
      AND b.date_of_construction IS NOT NULL
      AND b.current_use = '1_residential'
    """

    df_train = pd.read_sql(train_sql, conn)

    cases = {
        "consumo": _fit_tree_and_case(
            df_train=df_train,
            feature_names=feature_names,
            target_col="qual_consum",
            print_human_rules=print_human_rules
        ),
        "emisiones": _fit_tree_and_case(
            df_train=df_train,
            feature_names=feature_names,
            target_col="qual_emissions",
            print_human_rules=print_human_rules
        )
    }

    if print_qgis_case:
        print("\nQGIS CASE (consumo):\n")
        print(cases["consumo"])
        print("\nQGIS CASE (emisiones):\n")
        print(cases["emisiones"])

    return cases