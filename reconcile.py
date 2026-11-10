"""Cross-check for the Power Query reconciliation: same logic in pandas.

Lines up model NOI against accounting actuals by deal ID, keeps deals that
appear in only one file (full outer join), and flags anything off by more
than the tolerance. Run: python reconcile.py
"""
import pandas as pd

TOLERANCE = 0.10  # $M

model = pd.read_csv("data/model_noi.csv").rename(
    columns={"Deal ID": "deal_id", "Model NOI ($M)": "model_noi"})
actuals = pd.read_csv("data/accounting_actuals.csv").rename(
    columns={"actual_noi_musd": "actual_noi"}).drop(columns="period")

recon = model.merge(actuals, on="deal_id", how="outer", indicator=True)
recon["variance"] = (recon["actual_noi"] - recon["model_noi"]).round(2)
recon["status"] = "OK"
recon.loc[recon["variance"].abs() > TOLERANCE, "status"] = "VARIANCE"
recon.loc[recon["_merge"] == "left_only", "status"] = "MISSING: not in accounting"
recon.loc[recon["_merge"] == "right_only", "status"] = "MISSING: not in model"

breaks = (recon[recon["status"] != "OK"]
          .assign(size=lambda df: df["variance"].abs())
          .sort_values(["status", "size"], ascending=[False, False])
          [["deal_id", "Deal Name", "model_noi", "actual_noi", "variance", "status"]])
print(f"{len(recon)} deals checked, {len(breaks)} breaks (tolerance ${TOLERANCE}M)\n")
print(breaks.to_string(index=False))
