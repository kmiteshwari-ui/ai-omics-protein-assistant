import requests


def get_protein_info(protein_id):
    url = f"https://rest.uniprot.org/uniprotkb/{protein_id}.json"

    response = requests.get(url, timeout=15)

    if response.status_code != 200:
        return None

    data = response.json()

    # Protein name
    protein_name = (
        data.get("proteinDescription", {})
        .get("recommendedName", {})
        .get("fullName", {})
        .get("value", "Not available")
    )

    # Organism
    organism = data.get("organism", {}).get(
        "scientificName", "Not available"
    )

    # Sequence length
    sequence = data.get("sequence", {})
    length = sequence.get("length", "Not available")

    # Gene name
    genes = data.get("genes", [])
    gene_name = "Not available"

    if genes:
        gene_name = (
            genes[0]
            .get("geneName", {})
            .get("value", "Not available")
        )

    # Function
    function = "Not available"

    for comment in data.get("comments", []):
        if comment.get("commentType") == "FUNCTION":

            texts = comment.get("texts", [])

            if texts:
                function = " ".join(
                    text.get("value", "")
                    for text in texts
                    if text.get("value")
                )

            # Alternative format
            if function == "Not available":
                function = comment.get(
                    "text", {}
                ).get("value", "Not available")

            break

    # GO terms
    go_terms = []

    for reference in data.get("uniProtKBCrossReferences", []):
        if reference.get("database") == "GO":
            properties = reference.get("properties", [])

            for prop in properties:
                if prop.get("key") == "GoTerm":
                    go_terms.append(prop.get("value"))

    if not go_terms:
        go_terms = ["Not available"]

    return {
        "protein_id": protein_id,
        "protein_name": protein_name,
        "gene_name": gene_name,
        "organism": organism,
        "length": length,
        "function": function,
        "go_terms": go_terms,
    }
