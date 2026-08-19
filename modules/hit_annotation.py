import requests
import re


def extract_uniprot_id(target):
    """
    Try to extract a UniProt accession from a Foldseek target.
    """

    if not target:
        return None

    # Common UniProt accession patterns
    patterns = [
        r"\b[A-NR-Z][0-9][A-Z0-9]{3}[0-9]\b",
        r"\b[A-Z0-9]{6,10}\b"
    ]

    for pattern in patterns:
        match = re.search(pattern, target)

        if match:
            return match.group(0)

    return None


def get_hit_annotation(target):

    uniprot_id = extract_uniprot_id(target)

    if not uniprot_id:
        return {
            "uniprot_id": None,
            "protein_name": "Not available",
            "function": "Not available",
            "organism": "Not available"
        }

    url = (
        f"https://rest.uniprot.org/"
        f"uniprotkb/{uniprot_id}.json"
    )

    try:

        response = requests.get(
            url,
            timeout=20
        )

        if response.status_code != 200:

            return {
                "uniprot_id": uniprot_id,
                "protein_name": "Not available",
                "function": "Not available",
                "organism": "Not available"
            }

        data = response.json()

        protein_name = (
            data.get("proteinDescription", {})
            .get("recommendedName", {})
            .get("fullName", {})
            .get("value", "Not available")
        )

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

                break

        organism = (
            data.get("organism", {})
            .get("scientificName", "Not available")
        )

        return {
            "uniprot_id": uniprot_id,
            "protein_name": protein_name,
            "function": function,
            "organism": organism
        }

    except requests.RequestException:

        return {
            "uniprot_id": uniprot_id,
            "protein_name": "Not available",
            "function": "Not available",
            "organism": "Not available"
        }
