import pandas as pd
import numpy as np
from scipy.stats import ttest_ind


def analyze_biomarkers(df):
    """
    Run biomarker statistics (fold change, Welch's t-test, BH-adjusted
    p-value, biomarker score) across every gene in the uploaded dataset.

    Expected format:

    Gene,H1,H2,H3,D1,D2,D3
    CDK1,10,12,11,45,48,43

    This is kept as an internal building block — BH correction is only
    statistically meaningful across the full set of genes tested, so
    analyze_single_protein() below runs this first and then extracts
    just the one gene of interest.
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
    within the full biomarker results table.

    Returns a dict of that gene's row, or None if the gene isn't
    present in the dataset, or no gene name is available at all.
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


def analyze_single_protein(df, target_gene):
    """
    Entry point for the app: given the uploaded expression CSV and the
    gene name of the protein currently being searched, return biomarker
    evidence for THAT gene only.

    Statistics (fold change, Welch's t-test, BH-adjusted p-value) are
    still computed across the full dataset internally, since adjusted
    p-values are only meaningful in the context of all genes tested —
    but only target_gene's evidence is ever returned to the caller.

    Returns:
        dict  — evidence for target_gene, if the CSV is valid and the
                gene is present in it.
        None  — if the CSV is invalid/unusable, no target_gene was
                provided, or target_gene isn't present in the dataset.
    """

    if not target_gene or target_gene == "Not available":
        return None

    full_results = analyze_biomarkers(df)

    if full_results is None:
        return None

    return get_gene_evidence(full_results, target_gene)
