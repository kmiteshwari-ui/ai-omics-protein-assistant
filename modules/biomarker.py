import pandas as pd
import numpy as np
from scipy.stats import ttest_ind


def analyze_single_protein(
    df,
    target_gene
):
    """
    Analyze biomarker evidence for the specific
    gene/protein searched by the user.

    Expected CSV:
    Gene,H1,H2,H3,D1,D2,D3
    """

    if "Gene" not in df.columns:
        return None

    healthy_cols = [
        col for col in df.columns
        if col.startswith("H")
    ]

    disease_cols = [
        col for col in df.columns
        if col.startswith("D")
    ]

    if len(healthy_cols) < 2 or len(disease_cols) < 2:
        return None

    target_gene = target_gene.strip().upper()

    matches = df[
        df["Gene"].astype(str).str.upper() == target_gene
    ]

    if matches.empty:
        return None

    row = matches.iloc[0]

    healthy = pd.to_numeric(
        row[healthy_cols],
        errors="coerce"
    ).dropna().values

    disease = pd.to_numeric(
        row[disease_cols],
        errors="coerce"
    ).dropna().values

    if len(healthy) < 2 or len(disease) < 2:
        return None

    healthy_mean = np.mean(healthy)
    disease_mean = np.mean(disease)

    fold_change = (
        disease_mean + 0.01
    ) / (
        healthy_mean + 0.01
    )

    log2_fc = np.log2(fold_change)

    _, p_value = ttest_ind(
        disease,
        healthy,
        equal_var=False
    )

    candidate = (
        abs(log2_fc) >= 1
        and p_value < 0.05
    )

    return {
        "gene": target_gene,
        "healthy_mean": healthy_mean,
        "disease_mean": disease_mean,
        "fold_change": fold_change,
        "log2_fold_change": log2_fc,
        "p_value": p_value,
        "potential_biomarker": candidate
    }
