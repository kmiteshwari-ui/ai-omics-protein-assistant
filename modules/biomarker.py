import pandas as pd
import numpy as np
from scipy.stats import ttest_ind


def analyze_single_protein(df, target_gene):
    """Analyze biomarker evidence for the searched protein."""

    if "Gene" not in df.columns:
        return None

    healthy_cols = [
        col for col in df.columns
        if str(col).upper().startswith("H")
    ]

    disease_cols = [
        col for col in df.columns
        if str(col).upper().startswith("D")
    ]

    if len(healthy_cols) < 2 or len(disease_cols) < 2:
        return None

    target_gene = str(target_gene).strip().upper()

    matches = df[
        df["Gene"].astype(str).str.strip().str.upper()
        == target_gene
    ]

    if matches.empty:
        return None

    row = matches.iloc[0]

    healthy = pd.to_numeric(
        row[healthy_cols], errors="coerce"
    ).dropna().values

    disease = pd.to_numeric(
        row[disease_cols], errors="coerce"
    ).dropna().values

    if len(healthy) < 2 or len(disease) < 2:
        return None

    healthy_mean = float(np.mean(healthy))
    disease_mean = float(np.mean(disease))

    fold_change = (
        (disease_mean + 0.01) /
        (healthy_mean + 0.01)
    )

    log2_fc = float(np.log2(fold_change))

    _, p_value = ttest_ind(
        disease,
        healthy,
        equal_var=False
    )

    potential_biomarker = (
        abs(log2_fc) >= 1 and
        p_value < 0.05
    )

    return {
        "gene": target_gene,
        "healthy_mean": healthy_mean,
        "disease_mean": disease_mean,
        "fold_change": float(fold_change),
        "log2_fold_change": log2_fc,
        "p_value": float(p_value),
        "potential_biomarker": potential_biomarker
    }


def analyze_biomarkers(df):
    """
    Analyze all genes in the uploaded dataset.
    Kept for compatibility with the previous app.
    """

    if "Gene" not in df.columns:
        return None

    healthy_cols = [
        col for col in df.columns
        if str(col).upper().startswith("H")
    ]

    disease_cols = [
        col for col in df.columns
        if str(col).upper().startswith("D")
    ]

    if len(healthy_cols) < 2 or len(disease_cols) < 2:
        return None

    results = []

    for _, row in df.iterrows():

        gene = str(row["Gene"])

        healthy = pd.to_numeric(
            row[healthy_cols], errors="coerce"
        ).dropna().values

        disease = pd.to_numeric(
            row[disease_cols], errors="coerce"
        ).dropna().values

        if len(healthy) < 2 or len(disease) < 2:
            continue

        healthy_mean = np.mean(healthy)
        disease_mean = np.mean(disease)

        fold_change = (
            (disease_mean + 0.01) /
            (healthy_mean + 0.01)
        )

        log2_fc = np.log2(fold_change)

        _, p_value = ttest_ind(
            disease,
            healthy,
            equal_var=False
        )

        results.append({
            "Gene": gene,
            "Healthy Mean": healthy_mean,
            "Disease Mean": disease_mean,
            "Fold Change": fold_change,
            "Log2 Fold Change": log2_fc,
            "P-value": p_value
        })

    if not results:
        return None

    results = pd.DataFrame(results)

    results = results.sort_values("P-value")

    n = len(results)

    results["Adjusted P-value"] = [
        min(
            p * n / (i + 1),
            1.0
        )
        for i, p in enumerate(
            results["P-value"]
        )
    ]

    results["Biomarker Score"] = (
        abs(results["Log2 Fold Change"]) *
        -np.log10(
            results["Adjusted P-value"] + 1e-300
        )
    )

    results["Candidate"] = np.where(
        (
            (abs(results["Log2 Fold Change"]) >= 1)
            &
            (results["Adjusted P-value"] < 0.05)
        ),
        "Potential Candidate",
        "Low Evidence"
    )

    return results.sort_values(
        "Biomarker Score",
        ascending=False
    )
