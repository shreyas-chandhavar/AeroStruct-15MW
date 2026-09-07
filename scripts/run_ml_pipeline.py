#!/usr/bin/env python3
from __future__ import annotations
import argparse, time
from pathlib import Path
import numpy as np
import pandas as pd
from aerostruct15mw.config import BASELINE_DEL10_PROXY_MNM, TurbineConfig
from aerostruct15mw.io import load_processed_reference_data
from aerostruct15mw.ml import lhs_designs, fit_surrogates, surrogate_predict
from aerostruct15mw.pareto import apply_engineering_constraints, core_pareto_front, select_utopia_design
from aerostruct15mw.physics import PhysicsEvaluator
ROOT = Path(__file__).resolve().parents[1]

def build_evaluator():
    cfg = TurbineConfig()
    geometry, structural = load_processed_reference_data(ROOT / "data" / "processed")
    span = geometry["span_m"].to_numpy(); struct_span = structural["span_fraction"].to_numpy() * geometry["span_m"].max()
    flap = np.interp(span, struct_span, structural["flap_EI_Nm2"]); edge = np.interp(span, struct_span, structural["edge_EI_Nm2"]); mass = np.interp(span, struct_span, structural["mass_density_kgpm"])
    return PhysicsEvaluator(geometry, span, flap, edge, mass, ROOT / "data" / "reference" / "airfoils", cfg)

def evaluate_designs(evaluator, designs):
    rows = []; t0 = time.time()
    for i, row in designs.iterrows():
        rows.append(evaluator.evaluate(row.peak_twist_deg, row.aero_start_m, row.struct_start_m, row.EI_increase_percent))
        if (i + 1) % 25 == 0: print(f"Physics evaluated {i+1}/{len(designs)} | elapsed {(time.time()-t0)/60:.2f} min")
    return pd.DataFrame(rows)

def main():
    parser = argparse.ArgumentParser(); parser.add_argument("--training-designs", type=int, default=300); parser.add_argument("--search-designs", type=int, default=100000); parser.add_argument("--verify-pareto", action="store_true"); args = parser.parse_args()
    evaluator = build_evaluator(); out = ROOT / "results" / "tables"; out.mkdir(parents=True, exist_ok=True)
    doe = lhs_designs(args.training_designs, seed=42); database = evaluate_designs(evaluator, doe); database.to_csv(out / "physics_database.csv", index=False)
    fit = fit_surrogates(database); fit.holdout_metrics.to_csv(out / "surrogate_holdout_metrics.csv", index=False); fit.cv_metrics.to_csv(out / "surrogate_cv_metrics.csv", index=False)
    search = lhs_designs(args.search_designs, seed=123); predicted = surrogate_predict(search, fit.best_models); feasible = apply_engineering_constraints(predicted); pareto = core_pareto_front(feasible); pareto.to_csv(out / "surrogate_core_pareto.csv", index=False)
    print(f"Search designs: {len(search)}"); print(f"Physics-constrained surrogate designs: {len(feasible)}"); print(f"Core surrogate Pareto designs: {len(pareto)}")
    if args.verify_pareto:
        verified = evaluate_designs(evaluator, pareto[["peak_twist_deg", "aero_start_m", "struct_start_m", "EI_increase_percent"]]); verified = apply_engineering_constraints(verified); verified = core_pareto_front(verified); verified.to_csv(out / "physics_verified_pareto.csv", index=False)
        fatigue_ok = verified[verified["DEL10_proxy_MNm"] <= 1.01 * BASELINE_DEL10_PROXY_MNM]; selected, scored = select_utopia_design(fatigue_ok); scored.to_csv(out / "physics_verified_pareto_scored.csv", index=False); print("Selected balanced design:"); print(selected)

if __name__ == "__main__":
    main()
