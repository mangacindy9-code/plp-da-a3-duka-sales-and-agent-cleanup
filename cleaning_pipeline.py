"""Reusable cleaning pipeline for the mobile-money agent transaction extract."""
import pandas as pd

TYPE_MAP = {"deposit": "Deposit", "withdrawal": "Withdrawal"}


def clean_agent_data(txns, agents):
    """Clean the agent transaction extract and merge it with the agent register.

    Rules applied, in order: strip whitespace, remove duplicate txn_id values,
    standardise txn_type, parse dates (ISO and slash formats), convert amount to
    numeric, flag IQR outliers, impute missing/invalid amounts with the median
    for the same txn_type (flagged), and left-join the agent register.

    Parameters
    ----------
    txns : pandas.DataFrame
        Raw transactions (txn_id, agent_id, txn_type, amount, txn_date).
    agents : pandas.DataFrame
        Agent register (agent_id, county, onboarded).

    Returns
    -------
    clean_df : pandas.DataFrame
        Cleaned transactions with columns amount_imputed, is_outlier,
        unknown_agent and county (unknown agents get county "Unknown").
    log : pandas.DataFrame
        One row per cleaning step: step, rule, rows_affected, decision.
    """
    log = []

    def record(step, rule, n, decision=""):
        log.append({"step": step, "rule": rule,
                    "rows_affected": int(n), "decision": decision})

    df = txns.copy()
    ag = agents.copy()
    record("0 Input", "Raw transaction rows", len(df))

    # 1. Whitespace in text columns
    for col in ["txn_id", "agent_id", "txn_type"]:
        stripped = df[col].astype("string").str.strip()
        changed = (stripped != df[col].astype("string")).sum()
        df[col] = stripped
        record("1 Consistency", f"Strip whitespace in {col}", changed)

    # 2. Uniqueness: txn_id must be unique
    dup = df.duplicated(subset="txn_id", keep="first")
    df = df.loc[~dup].copy()
    record("2 Uniqueness", "Drop repeated txn_id (keep first)", dup.sum(),
           "Repeated records of the same transaction are double counting")

    # 3. txn_type -> exactly Deposit / Withdrawal
    std = df["txn_type"].str.lower().map(TYPE_MAP)
    record("3 Consistency", "Standardise txn_type case", (std != df["txn_type"]).sum())
    record("3 Validity", "txn_type not mappable (left missing)", std.isna().sum())
    df["txn_type"] = std

    # 4. Dates: accept YYYY-MM-DD and YYYY/MM/DD
    raw_date = df["txn_date"].astype("string").str.strip()
    record("4 Consistency", "Dates written with '/' converted to '-'",
           raw_date.str.contains("/", na=False).sum())
    parsed = pd.to_datetime(raw_date.str.replace("/", "-", regex=False),
                            format="%Y-%m-%d", errors="coerce")
    record("4 Validity", "Unparseable dates", parsed.isna().sum())
    df["txn_date"] = parsed

    # 5. Amount -> numeric
    raw_amt = df["amount"]
    amt = pd.to_numeric(raw_amt, errors="coerce")
    record("5 Validity", "Non-numeric amount text set to missing",
           (raw_amt.notna() & amt.isna()).sum())
    nonpos = amt <= 0
    amt = amt.mask(nonpos)
    record("5 Validity", "Zero/negative amounts set to missing", nonpos.sum())

    # 6. Outliers (IQR, computed on valid amounts only)
    q1, q3 = amt.quantile([0.25, 0.75])
    iqr = q3 - q1
    lo, hi = q1 - 1.5 * iqr, q3 + 1.5 * iqr
    df["is_outlier"] = (amt < lo) | (amt > hi)
    record("6 Accuracy", "IQR outliers flagged (kept, not removed)",
           df["is_outlier"].sum(), f"Fences: {lo:,.0f} to {hi:,.0f}")

    # 7. Missing amounts: median imputation by txn_type, with flag
    df["amount_imputed"] = amt.isna()
    med = amt.groupby(df["txn_type"]).transform("median")
    df["amount"] = amt.fillna(med)
    record("7 Completeness", "Missing amounts imputed with txn_type median",
           df["amount_imputed"].sum(), "Flagged in amount_imputed")

    # 8. Merge with the agent register (left join keeps every transaction)
    ag["agent_id"] = ag["agent_id"].astype("string").str.strip()
    ag = ag.drop_duplicates("agent_id")
    ag["onboarded"] = pd.to_datetime(ag["onboarded"], errors="coerce")
    n_before = len(df)
    merged = df.merge(ag[["agent_id", "county", "onboarded"]], on="agent_id",
                      how="left", validate="m:1", indicator=True)
    merged["unknown_agent"] = merged["_merge"].eq("left_only")
    merged["county"] = merged["county"].fillna("Unknown")
    merged = merged.drop(columns="_merge")
    assert len(merged) == n_before, "Merge changed the row count"
    record("8 Validity", "Transactions with agent_id not in register",
           merged["unknown_agent"].sum(),
           "Kept; county set to 'Unknown' and flagged in unknown_agent")

    record("9 Output", "Clean transaction rows", len(merged))
    return merged.reset_index(drop=True), pd.DataFrame(log)
