from __future__ import annotations

from dataclasses import dataclass

import numpy as np
import pandas as pd
from scipy.stats import qmc
from sklearn.base import clone
from sklearn.ensemble import ExtraTreesRegressor, GradientBoostingRegressor, RandomForestRegressor
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
from sklearn.model_selection import KFold, cross_val_score, train_test_split

from .config import DesignBounds

FEATURES = ["peak_twist_deg", "aero_start_m", "struct_start_m", "EI_increase_percent"]
TARGETS = ["rated_Cp", "rated_root_moment_MNm", "rated_tip_deflection_m", "gust_root_moment_MNm", "DEL10_proxy_MNm", "flap_3P_margin_Hz", "added_mass_kg"]


def lhs_designs(n=300, seed=42, bounds: DesignBounds | None = None) -> pd.DataFrame:
    bounds = bounds or DesignBounds()
    lo = np.array([bounds.peak_twist_deg[0], bounds.aero_start_m[0], bounds.struct_start_m[0], bounds.ei_increase_percent[0]])
    hi = np.array([bounds.peak_twist_deg[1], bounds.aero_start_m[1], bounds.struct_start_m[1], bounds.ei_increase_percent[1]])
    unit = qmc.LatinHypercube(d=4, seed=seed).random(n=n)
    x = qmc.scale(unit, lo, hi)
    return pd.DataFrame(x, columns=FEATURES)


def model_candidates(random_state=42):
    return {
        "Random Forest": RandomForestRegressor(n_estimators=400, random_state=random_state, n_jobs=-1),
        "Extra Trees": ExtraTreesRegressor(n_estimators=400, random_state=random_state, n_jobs=-1),
        "Gradient Boosting": GradientBoostingRegressor(n_estimators=300, learning_rate=0.04, max_depth=3, random_state=random_state),
    }


@dataclass
class SurrogateFit:
    models: dict
    holdout_metrics: pd.DataFrame
    cv_metrics: pd.DataFrame
    best_models: dict


def fit_surrogates(database: pd.DataFrame, test_size=0.20, random_state=42, cv_folds=5) -> SurrogateFit:
    x = database[FEATURES]
    x_train, x_test, train_idx, test_idx = train_test_split(x, np.arange(len(database)), test_size=test_size, random_state=random_state)
    models_by_target = {}
    holdout_rows = []
    cv_rows = []
    kfold = KFold(n_splits=cv_folds, shuffle=True, random_state=random_state)

    for target in TARGETS:
        y = database[target]
        y_train = y.iloc[train_idx]
        y_test = y.iloc[test_idx]
        models_by_target[target] = {}
        for name, proto in model_candidates(random_state).items():
            model = clone(proto)
            model.fit(x_train, y_train)
            pred = model.predict(x_test)
            holdout_rows.append({"target": target, "model": name, "R2": r2_score(y_test, pred), "MAE": mean_absolute_error(y_test, pred), "RMSE": np.sqrt(mean_squared_error(y_test, pred))})
            cv_scores = cross_val_score(clone(proto), x, y, cv=kfold, scoring="r2", n_jobs=-1)
            cv_rows.append({"target": target, "model": name, "CV_R2_mean": cv_scores.mean(), "CV_R2_std": cv_scores.std(), "CV_R2_min": cv_scores.min(), "CV_R2_max": cv_scores.max()})
            models_by_target[target][name] = model

    holdout = pd.DataFrame(holdout_rows)
    cv = pd.DataFrame(cv_rows)
    best = {}
    for target in TARGETS:
        best_row = cv[cv["target"] == target].sort_values("CV_R2_mean", ascending=False).iloc[0]
        best[target] = models_by_target[target][best_row["model"]]
    return SurrogateFit(models_by_target, holdout, cv, best)


def surrogate_predict(designs: pd.DataFrame, best_models: dict) -> pd.DataFrame:
    out = designs.copy()
    x = out[FEATURES]
    for target, model in best_models.items():
        out[target] = model.predict(x)
    return out
