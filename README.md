# NOI Reconciliation: Model vs. Accounting Actuals

A repeatable quarter-end check: line up each deal's **modeled net operating income (NOI)** against the **actuals from the accounting system**, and list every deal that doesn't match. Built in Excel **Power Query**, with a pandas script that confirms the same answer.

The data is made up: 15 deals across four funds, in the shape a real estate investment manager would see (a model extract, plus an export from a property accounting system like Yardi).

## The problem

Every quarter, the property models and the accounting system have to agree before results roll up to fund-level reporting. Two kinds of break matter:

| Break | Example | Why it happens |
|---|---|---|
| **Variance** | Model says $9.5M, actuals say $9.1M | Timing, a one-time accrual, an assumption that needs updating |
| **Missing** | A deal is in one file but not the other | A new acquisition not yet modeled, a sold asset still in the model, an ID mapping error |

A lookup in one direction only catches half the missing deals. This uses a **full outer join**, so a deal missing from *either* side shows up.

## Result

```
16 deals checked, 5 breaks (tolerance $0.1M)

deal_id   Deal Name                 model_noi  actual_noi  variance  status
D14       Columbus DC Campus        9.5        9.10        -0.40     VARIANCE
D07       Lydian Bridge Loan        5.9        5.62        -0.28     VARIANCE
D03       Riverwalk Office          2.1        1.95        -0.15     VARIANCE
D16                                            2.25                  MISSING: not in model
D12       Austin Construction Loan  1.2                              MISSING: not in accounting
```

D09 differs by only $0.01M, inside the tolerance, so it's correctly not flagged.

## How it's built in Power Query

1. **Load both files as connections** (Data > Get Data > From Text/CSV > Transform Data). Set Deal ID to text and NOI to decimal.
2. **Clean the accounting file:** drop the period column, rename the headers to match the model's.
3. **Merge** the two queries on Deal ID with **Join Kind: Full Outer**, then expand the accounting columns.
4. **Add two custom columns:**
   - `Variance = [Actual NOI] - [Model NOI ($M)]`
   - `Break = if either Deal ID is null then "MISSING" else if Number.Abs([Variance]) > 0.1 then "VARIANCE" else "OK"`
5. **Filter out "OK"** and load the result to a sheet.

**The point of doing it in Power Query rather than formulas:** next quarter, drop in the new exports and click **Refresh All**. Changing one value in the accounting file (D09 from 2.71 to 2.50) and refreshing adds it as a sixth break, with no formulas to rebuild.

## Files

| File | What it is |
|---|---|
| `data/model_noi.csv` | Model extract: deal ID, name, fund, modeled NOI ($M) |
| `data/accounting_actuals.csv` | Accounting export: deal ID, period, actual NOI ($M) |
| `reconcile.py` | The same reconciliation in pandas, as an independent check: `python reconcile.py` |

## What I'd add for production use

- A **log of each break's cause** (timing, mapping, accrual), so recurring breaks get fixed at the source instead of patched every quarter.
- **Sort by dollar size**, so the biggest breaks get looked at first.
- A **tolerance in percent as well as dollars**, so small deals aren't held to the same dollar threshold as large ones.

---
Built with AI coding assistance under my direction. I designed the checks and verified every output.
