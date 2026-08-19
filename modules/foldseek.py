import requests
import time


FOLDSEEK_URL = "https://search.foldseek.com/api"


def get_structure_content(structure_url):
    """
    Download structure file bytes (PDB format) from a given URL.
    Works for both experimental PDB URLs and AlphaFold URLs.
    """

    try:
        response = requests.get(structure_url, timeout=30)

        if response.status_code != 200:
            return None

        return response.content

    except requests.RequestException:
        return None


def search_foldseek(structure_url, protein_id, max_results=5):
    """
    Run a Foldseek structural similarity search.

    structure_url: URL to the structure file to search with
                    (either an experimental PDB or an AlphaFold model).
    protein_id:    used only for labeling the uploaded query file.
    """

    pdb_content = get_structure_content(structure_url)

    if not pdb_content:
        return None

    # Submit structure
    files = {
        "q": (
            f"{protein_id}.pdb",
            pdb_content,
            "application/octet-stream"
        )
    }

    data = [
        ("mode", "3diaa"),
        ("database[]", "pdb100")
    ]

    try:
        response = requests.post(
            f"{FOLDSEEK_URL}/ticket",
            files=files,
            data=data,
            timeout=60
        )
    except requests.RequestException:
        return None

    if response.status_code != 200:
        return None

    try:
        ticket = response.json()
    except ValueError:
        return None

    ticket_id = ticket.get("id")

    if not ticket_id:
        return None

    # Poll until complete
    for _ in range(30):

        try:
            status_response = requests.get(
                f"{FOLDSEEK_URL}/ticket/{ticket_id}",
                timeout=30
            )
        except requests.RequestException:
            return None

        if status_response.status_code != 200:
            return None

        try:
            status = status_response.json().get("status")
        except ValueError:
            return None

        if status == "ERROR":
            return None

        if status == "COMPLETE":
            break

        time.sleep(3)

    else:
        # Loop finished without breaking -> timed out
        return None

    # Get results
    try:
        result_response = requests.get(
            f"{FOLDSEEK_URL}/result/{ticket_id}/0",
            timeout=60
        )
    except requests.RequestException:
        return None

    if result_response.status_code != 200:
        return None

    try:
        result_data = result_response.json()
    except ValueError:
        return None

    return parse_results(result_data, max_results)


def parse_results(result_data, max_results):

    hits = []

    for result_group in result_data.get("results", []):

        for alignment_group in result_group.get(
            "alignments", []
        ):

            alignments = alignment_group

            if isinstance(alignments, dict):
                alignments = [alignments]

            for alignment in alignments:

                hits.append({
                    "target": alignment.get(
                        "target", "Unknown"
                    ),
                    "sequence_identity": alignment.get(
                        "seqId"
                    ),
                    "e_value": alignment.get(
                        "eval"
                    ),
                    "score": alignment.get(
                        "score"
                    ),
                    "alignment_length": alignment.get(
                        "alnLength"
                    )
                })

    return hits[:max_results]
