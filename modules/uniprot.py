import requests


def get_protein_info(protein_id):
    url = f"https://rest.uniprot.org/uniprotkb/{protein_id}.json"

    try:
        response = requests.get(url, timeout=15)
    except requests.RequestException as e:
        return None, f"Connection error reaching UniProt: {e}"

    if response.status_code == 404:
        return None, f"'{protein_id}' was not found on UniProt."

    if response.status_code != 200:
        return None, (
            f"UniProt returned an unexpected status "
            f"({response.status_code}). It may be temporarily "
            f"unavailable — try again in a moment."
        )

    try:
        data = response.json()
    except ValueError:
        return None, "UniProt returned an unreadable response."

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

    # ------------------------------------------------
    # Function
    # ------------------------------------------------
    # Preferred source: a free-text "FUNCTION" comment.
    # ------------------------------------------------

    function = "Not available"
    function_source = None

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

            if function != "Not available":
                function_source = "function_comment"

            break

    # ------------------------------------------------
    # Fallback source: "CATALYTIC ACTIVITY" comment.
    # Many well-annotated enzyme entries (e.g. LacZ /
    # beta-galactosidase, P00722) don't carry a separate
    # FUNCTION comment at all — their function is expressed
    # only through the reaction they catalyze.
    # ------------------------------------------------

    if function == "Not available":

        for comment in data.get("comments", []):

            if comment.get("commentType") == "CATALYTIC ACTIVITY":

                reaction = comment.get("reaction", {})
                reaction_text = reaction.get("name")

                if reaction_text:
                    function = (
                        f"Catalyzes the reaction: {reaction_text}"
                    )
                    function_source = "catalytic_activity"
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
        "function_source": function_source,
        "go_terms": go_terms,
    }, None
