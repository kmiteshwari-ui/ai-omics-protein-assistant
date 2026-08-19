import requests
import pandas as pd
import numpy as np


EXPRESSION_ATLAS_API = (
    "https://www.ebi.ac.uk/gxa/api"
)

DISEASE_EFO = "EFO_0000408"


def fetch_expression_atlas(
    gene,
    timeout=30
):
    """
    Fetch disease-associated differential-expression
    evidence for a human gene from EMBL-EBI
    Expression Atlas.

    Returns a list of disease-associated
    differential-expression observations.
    """

    if not gene:
        return None

    gene = str(gene).strip()

    if not gene:
        return None

    params = {
        "geneIs": gene,
        "updownIn": DISEASE_EFO,
        "format": "json"
    }

    try:

        response = requests.get(
            EXPRESSION_ATLAS_API,
            params=params,
            timeout=timeout
        )

        response.raise_for_status()

        data = response.json()

    except (
        requests.RequestException,
        ValueError
    ):

        return None

    return data


def _extract_results(data):
    """
    Expression Atlas has used slightly different
    response structures over time. This helper
    safely extracts the result records.
    """

    if not isinstance(data, dict):
        return []

    results = data.get(
        "results",
        []
    )

    if isinstance(results, list):
        return results

    return []


def _extract_gene_name(record):
    gene_data = record.get(
        "gene",
        {}
    )

    if isinstance(gene_data, dict):

        return (
            gene_data.get("name")
            or gene_data.get("id")
            or "Unknown"
        )

    return "Unknown"


def _extract_disease_expression(
    record
):
    """
    Convert Expression Atlas expression records
    into a simple dataframe-friendly structure.
    """

    expression_records = record.get(
        "expressions",
        []
    )

    if not isinstance(
        expression_records,
        list
    ):
        return []


    rows = []


    for expression in expression_records:

        if not isinstance(
            expression,
            dict
        ):
            continue


        disease = expression.get(
            "efoTerm",
            "Disease-associated condition"
        )

        efo_id = expression.get(
            "efoId",
            ""
        )

        up_experiments = expression.get(
            "upExperiments",
            0
        )

        down_experiments = expression.get(
            "downExperiments",
            0
        )

        non_de_experiments = expression.get(
            "nonDEExperiments",
            0
        )

        up_pvalue = expression.get(
            "upPvalue",
            np.nan
        )

        down_pvalue = expression.get(
            "downPvalue",
            np.nan
        )


        experiments = expression.get(
            "experiments",
            []
        )


        if isinstance(
            experiments,
            dict
        ):
            experiments = [
                experiments
            ]


        if not experiments:

            rows.append({

                "Disease": disease,

                "EFO ID": efo_id,

                "Direction": (
                    "UP"
                    if up_experiments > down_experiments
                    else "DOWN"
                    if down_experiments > up_experiments
                    else "Mixed"
                ),

                "Up Experiments": up_experiments,

                "Down Experiments": down_experiments,

                "Non-DE Experiments": (
                    non_de_experiments
                ),

                "Up P-value": up_pvalue,

                "Down P-value": down_pvalue,

                "Experiment": "Multiple Atlas experiments"

            })

            continue


        for experiment in experiments:

            if not isinstance(
                experiment,
                dict
            ):
                continue


            expression_direction = (
                experiment.get(
                    "expression",
                    "UNKNOWN"
                )
            )


            rows.append({

                "Disease": disease,

                "EFO ID": efo_id,

                "Direction": expression_direction,

                "Up Experiments": up_experiments,

                "Down Experiments": down_experiments,

                "Non-DE Experiments": (
                    non_de_experiments
                ),

                "Up P-value": up_pvalue,

                "Down P-value": down_pvalue,

                "Experiment": experiment.get(
                    "accession",
                    "Unknown"
                )

            })


    return rows


def analyze_single_protein(
    gene,
    timeout=30
):
    """
    Fetch disease-associated expression evidence
    for the searched protein's gene.

    No CSV upload is required.

    Returns a dictionary containing:

        gene
        evidence
        summary
        potential_biomarker
        direction
        best_p_value
    """

    if not gene:

        return None


    data = fetch_expression_atlas(
        gene,
        timeout=timeout
    )


    if data is None:

        return None


    results = _extract_results(
        data
    )


    if not results:

        return None


    all_rows = []


    for record in results:

        rows = _extract_disease_expression(
            record
        )

        all_rows.extend(
            rows
        )


    if not all_rows:

        return None


    df = pd.DataFrame(
        all_rows
    )


    # --------------------------------------
    # Direction summary
    # --------------------------------------

    up_count = int(
        (
            df["Direction"]
            .astype(str)
            .str.upper()
            == "UP"
        ).sum()
    )


    down_count = int(
        (
            df["Direction"]
            .astype(str)
            .str.upper()
            == "DOWN"
        ).sum()
    )


    if up_count > down_count:

        overall_direction = "Upregulated"

    elif down_count > up_count:

        overall_direction = "Downregulated"

    else:

        overall_direction = "Mixed"


    # --------------------------------------
    # Best p-value
    # --------------------------------------

    p_values = []


    for column in [
        "Up P-value",
        "Down P-value"
    ]:

        values = pd.to_numeric(
            df[column],
            errors="coerce"
        )

        p_values.extend(
            values.dropna().tolist()
        )


    if p_values:

        best_p_value = min(
            p_values
        )

    else:

        best_p_value = np.nan


    # --------------------------------------
    # Evidence strength
    # --------------------------------------

    total_disease_observations = len(
        df
    )


    significant = False


    if not np.isnan(
        best_p_value
    ):

        significant = (
            best_p_value <= 0.05
        )


    potential_biomarker = (
        total_disease_observations >= 1
        and significant
    )


    # --------------------------------------
    # Summary
    # --------------------------------------

    summary = (
        f"{gene} has "
        f"{total_disease_observations} "
        f"disease-associated expression "
        f"observation(s) in Expression Atlas. "
        f"The overall reported direction is "
        f"{overall_direction.lower()}."
    )


    return {

        "gene": gene,

        "evidence": df,

        "summary": summary,

        "potential_biomarker": (
            potential_biomarker
        ),

        "direction": overall_direction,

        "best_p_value": best_p_value,

        "source": (
            "EMBL-EBI Expression Atlas"
        ),

        "source_url": (
            "https://www.ebi.ac.uk/gxa/"
        )

    }
