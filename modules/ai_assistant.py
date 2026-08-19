from modules.biomarker import get_gene_evidence


def generate_protein_analysis(
    protein,
    alphafold=None,
    foldseek_results=None,
    biomarker_results=None
):
    report = []

    report.append("## 🤖 AI Research Assistant")

    report.append(
        f"### Protein: {protein['protein_name']}"
    )

    report.append(
        f"**Organism:** {protein['organism']}"
    )

    report.append(
        f"**Length:** {protein['length']} amino acids"
    )

    # ==========================================
    # Functional interpretation
    # ==========================================

    report.append("### 🔬 Functional Interpretation")

    top_hit = None

    if foldseek_results:
        top_hit = foldseek_results[0]

    if protein["function"] != "Not available":

        # Curated UniProt evidence (either a FUNCTION comment,
        # or a CATALYTIC ACTIVITY fallback — see modules/uniprot.py)
        source_label = (
            "UniProt annotation"
            if protein.get("function_source") == "function_comment"
            else "UniProt (catalytic activity)"
        )

        report.append(
            f"{source_label} indicates: "
            f"{protein['function']}"
        )

    elif top_hit and top_hit.get("function") and \
            top_hit.get("function") != "Not available":

        # No curated UniProt function at all — fall back to the
        # top Foldseek hit's annotated function as an inferred hypothesis.
        hit_name = top_hit.get(
            "protein_name", "an unidentified structural homolog"
        )

        seq_id = top_hit.get("sequence_identity", "N/A")

        report.append(
            "No curated UniProt functional annotation is available "
            "for this entry."
        )

        report.append(
            f"Based on structural similarity to **{hit_name}** "
            f"(Foldseek top hit, sequence identity: **{seq_id}**), "
            f"the inferred function is: {top_hit.get('function')}"
        )

        report.append(
            "_This is a structure-based functional hypothesis, "
            "not a curated annotation, and should be treated "
            "accordingly._"
        )

    else:
        report.append(
            "No functional description is currently available."
        )

    # ==========================================
    # AlphaFold
    # ==========================================

    report.append("### 🧊 Structural Evidence")

    if alphafold:

        plddt = alphafold.get("plddt")

        if plddt is not None:
            report.append(
                f"AlphaFold provides a predicted structure "
                f"with a pLDDT score of **{plddt}**."
            )

        report.append(
            "The predicted structure was further investigated "
            "using structural similarity analysis."
        )

    else:
        report.append(
            "AlphaFold information was not available."
        )

    # ==========================================
    # Foldseek
    # ==========================================

    report.append("### 🔎 Foldseek Evidence")

    if foldseek_results:

        report.append(
            f"Foldseek identified "
            f"**{len(foldseek_results)} structural hits**."
        )

        report.append(
            f"The top structural hit is "
            f"**{top_hit.get('target', 'Unknown')}**."
        )

        report.append(
            f"Sequence identity: "
            f"**{top_hit.get('sequence_identity', 'N/A')}**."
        )

        report.append(
            "Structural similarity can provide useful "
            "evidence for possible functional relationships, "
            "but it does not by itself prove function."
        )

    else:
        report.append(
            "No Foldseek hits were available."
        )

    # ==========================================
    # Biomarker analysis — tied to THIS protein's gene
    # ==========================================

    report.append("### 🧪 Biomarker Analysis")

    gene_name = protein.get("gene_name")

    if biomarker_results is None or biomarker_results.empty:

        report.append(
            "No biomarker dataset has been analyzed yet."
        )

    else:

        gene_evidence = get_gene_evidence(
            biomarker_results, gene_name
        )

        if gene_evidence is None:

            report.append(
                f"The uploaded expression dataset does not "
                f"contain data for **{gene_name}** "
                f"({protein['protein_name']}), so no biomarker "
                f"evidence is available for this specific protein "
                f"from this dataset."
            )

        else:

            report.append(
                f"Expression evidence for **{gene_name}** "
                f"({protein['protein_name']}) was found in the "
                f"uploaded dataset:"
            )

            report.append(
                f"- Healthy Mean: "
                f"**{gene_evidence['Healthy Mean']:.2f}**\n"
                f"- Disease Mean: "
                f"**{gene_evidence['Disease Mean']:.2f}**\n"
                f"- Fold Change: "
                f"**{gene_evidence['Fold Change']:.2f}**\n"
                f"- Log₂ Fold Change: "
                f"**{gene_evidence['Log2 Fold Change']:.2f}**\n"
                f"- Adjusted P-value: "
                f"**{gene_evidence['Adjusted P-value']:.4f}**"
            )

            if gene_evidence.get("Candidate") == "Potential Candidate":

                report.append(
                    f"**{gene_name}** meets the fold-change and "
                    f"significance thresholds in this dataset and "
                    f"is flagged as a **potential biomarker "
                    f"candidate**."
                )

            else:

                report.append(
                    f"**{gene_name}** does not meet the "
                    f"fold-change / significance thresholds in "
                    f"this dataset, so it is not flagged as a "
                    f"biomarker candidate here."
                )

            report.append(
                "This should be considered a research hypothesis "
                "rather than a clinically validated biomarker."
            )

    # ==========================================
    # Recommendations
    # ==========================================

    report.append("### 🔬 Recommended Next Steps")

    report.append(
        "1. Investigate the strongest structural similarity hits."
    )

    report.append(
        "2. Examine relevant GO terms and biological pathways."
    )

    report.append(
        "3. Validate promising biomarker candidates "
        "using an independent dataset."
    )

    report.append(
        "4. Consider experimental validation before "
        "drawing clinical conclusions."
    )

    return "\n\n".join(report)
