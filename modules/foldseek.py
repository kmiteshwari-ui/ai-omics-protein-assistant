import requests
import time


FOLDSEEK_URL = "https://search.foldseek.com/api"


def get_alphafold_pdb(protein_id):
    url = f"https://alphafold.ebi.ac.uk/files/AF-{protein_id}-F1-model_v6.pdb"

    response = requests.get(url, timeout=30)

    if response.status_code != 200:
        return None

    return response.content


def search_foldseek(protein_id, max_results=5):

    pdb_content = get_alphafold_pdb(protein_id)

    if not pdb_content:
        return None

    # Submit structure
    files = {
        "q": (
            f"AF-{protein_id}.pdb",
            pdb_content,
            "application/octet-stream"
        )
    }

    data = [
        ("mode", "3diaa"),
        ("database[]", "pdb100")
    ]

    response = requests.post(
        f"{FOLDSEEK_URL}/ticket",
        files=files,
        data=data,
        timeout=60
    )

    if response.status_code != 200:
        return None

    ticket = response.json()
    ticket_id = ticket.get("id")

    if not ticket_id:
        return None

    # Poll until complete
    for _ in range(30):

        status_response = requests.get(
            f"{FOLDSEEK_URL}/ticket/{ticket_id}",
            timeout=30
        )

        if status_response.status_code != 200:
            return None

        status = status_response.json().get("status")

        if status == "ERROR":
            return None

        if status == "COMPLETE":
            break

        time.sleep(3)

    else:
        return None

    # Get results
    result_response = requests.get(
        f"{FOLDSEEK_URL}/result/{ticket_id}/0",
        timeout=60
    )

    if result_response.status_code != 200:
        return None

    result_data = result_response.json()

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
