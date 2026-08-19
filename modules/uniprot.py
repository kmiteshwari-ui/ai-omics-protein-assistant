import requests


def get_protein_info(protein_id):
    url = f"https://rest.uniprot.org/uniprotkb/{protein_id}.json"

    response = requests.get(url, timeout=15)

    if response.status_code != 200:
        return None

    data = response.json()

    protein_name = (
        data.get("proteinDescription", {})
        .get("recommendedName", {})
        .get("fullName", {})
        .get("value", "Not available")
    )

    organism = data.get("organism", {}).get("scientificName", "Not available")

    sequence = data.get("sequence", {})

    function = "Not available"

    for comment in data.get("comments", []):
        if comment.get("commentType") == "FUNCTION":
            texts = comment.get("texts", [])
            if texts:
                function = texts[0].get("value", "Not available")
                break

    return {
        "protein_id": protein_id,
        "protein_name": protein_name,
        "organism": organism,
        "length": sequence.get("length", "Not available"),
        "function": function,
    }
