def generate_protein_analysis(protein, alphafold, foldseek_results):
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

    # Functional interpretation
    report.append("### 🔬 Functional Interpretation")

    if protein["function"] != "Not available":
        report.append(
            f"Based on UniProt annotation, this protein is "
            f"associated with: {protein['function']}"
        )
    else:
        report.append(
            "No curated functional description was available."
        )

    # AlphaFold interpretation
    report.append("### 🧊 Structural Evidence")

    if alphafold:
        plddt = alphafold.get("plddt")

        if plddt is not None:
            report.append(
                f"AlphaFold provides a predicted structure "
                f"with a pLDDT score of **{plddt}**."
            )

        report.append(
            "The predicted structure can be investigated "
            "further using structural similarity analysis."
        )
    else:
        report.append(
            "AlphaFold structural information was not available."
        )

    # Foldseek interpretation
    report.append("### 🔎 Foldseek Evidence")

    if foldseek_results:

        report.append(
            f"Foldseek identified **{len(foldseek_results)} "
            f"structural similarity hits**."
        )

        top_hit = foldseek_results[0]

        target = top_hit.get("target", "Unknown")
        evalue = top_hit.get("e_value", "N/A")
        seqid = top_hit.get("sequence_identity", "N/A")

        report.append(
            f"The top structural hit is **{target}**, "
            f"with sequence identity of **{seqid}** "
            f"and E-value of **{evalue}**."
        )

        report.append(
            "Structural similarity may provide evidence "
            "for possible functional relationships, but "
            "it should not be treated as definitive proof."
        )

    else:
        report.append(
            "No Foldseek structural hits were available."
        )

    # Biomarker interpretation
    report.append("### 🧪 Biomarker Perspective")

    report.append(
        "This protein could be considered for further "
        "biomarker investigation if it shows consistent "
        "differential expression between disease and "
        "healthy samples."
    )

    # Next steps
    report.append("### 🔬 Recommended Next Steps")

    report.append(
        "1. Compare expression between disease and healthy samples."
    )

    report.append(
        "2. Investigate relevant GO terms and pathways."
    )

    report.append(
        "3. Examine the strongest Foldseek structural hits."
    )

    report.append(
        "4. Validate promising candidates using an independent dataset."
    )

    return "\n\n".join(report)
