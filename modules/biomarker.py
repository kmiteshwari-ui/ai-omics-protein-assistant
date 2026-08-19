import pandas as pd
import numpy as np


def analyze_biomarkers(df):
    required_columns = {"Gene", "Healthy", "Disease"}

    if not required_columns.issubset(df.columns):
        return None

    results = df.copy()

    results["Healthy"] = pd.to_numeric(
        results["Healthy"], errors="coerce"
    )
    results["Disease"] = pd.to_numeric(
        results["Disease"], errors="coerce"
    )

    results = results.dropna()

    # Avoid division by zero
    results["Fold Change"] = (
        (results["Disease"] + 0.01) /
        (results["Healthy"] + 0.01)
    )

    results["Log2 Fold Change"] = np.log2(
        results["Fold Change"]
    )

    # Simple preliminary ranking score
    results["Biomarker Score"] = (
        abs(results["Log2 Fold Change"]) * 20
    ).clip(upper=100)

    results["Candidate"] = np.where(
        abs(results["Log2 Fold Change"]) >= 1,
        "Potential Candidate",
        "Low Evidence"
    )

    results = results.sort_values(
        "Biomarker Score",
        ascending=False
    )

    return results
