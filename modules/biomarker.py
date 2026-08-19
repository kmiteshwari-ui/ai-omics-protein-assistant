import pandas as pd
import numpy as np
from scipy.stats import ttest_ind


def analyze_biomarkers(df):
    """
    Expected format:

    Gene,H1,H2,H3,D1,D2,D3
    CDK1,10,12,11,45,48,43
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

    results = []

    for _, row in df.iterrows():

        gene = row["Gene"]

        healthy = pd.to_numeric(
            row[healthy_cols],
            errors="coerce"
        ).dropna().values

        disease = pd.to_numeric(
            row[disease_cols],
            errors="coerce"
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

        # Welch's t-test
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

    # Benjamini-Hochberg FDR correction
    results = results.sort_values("P-value")

    n = len(results)

    results["Adjusted P-value"] = [
        min(p * n / (i + 1), 1.0)
        for i, p in enumerate(
            results["P-value"]
        )
    ]

    # Biomarker score
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

    results = results.sort_values(
        "Biomarker Score",
        ascending=False
    )

    return results


def get_gene_evidence(results, gene_name):
    """
    Look up expression / biomarker evidence for ONE specific gene
    within the full biomarker results table — used to tie the
    uploaded expression dataset back to the protein currently
    being searched (via its UniProt gene name).

    Returns a dict of that gene's row (Healthy Mean, Disease Mean,
    Fold Change, Log2 Fold Change, P-value, Adjusted P-value,
    Biomarker Score, Candidate), or None if the gene isn't present
    in the uploaded dataset, or no gene name is available at all.
    """

    if results is None or results.empty:
        return None

    if not gene_name or gene_name == "Not available":
        return None

    matches = results[
        results["Gene"].astype(str).str.strip().str.upper()
        == str(gene_name).strip().upper()
    ]

    if matches.empty:
        return None

    return matches.iloc[0].to_dict()
