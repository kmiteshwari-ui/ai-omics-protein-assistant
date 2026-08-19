import requests
import time


FOLDSEEK_API = "https://search.foldseek.com/api"


def submit_structure(structure_url, protein_id):

    try:
        response = requests.get(
            structure_url,
            timeout=30
        )

        if response.status_code != 200:
            return None

        files = {
            "q": (
                f"{protein_id}.pdb",
                response.content,
                "application/octet-stream"
            )
        }

        data = [
            ("mode", "3diaa"),
            ("database[]", "pdb100")
        ]

        response = requests.post(
            f"{FOLDSEEK_API}/ticket",
            files=files,
            data=data,
            timeout=60
        )

        if response.status_code != 200:
            return None

        return response.json().get("id")

    except requests.RequestException:
        return None


def get_foldseek_results(ticket_id, max_results=5):

    for _ in range(30):

        try:

            response = requests.get(
                f"{FOLDSEEK_API}/ticket/{ticket_id}",
                timeout=30
            )

            if response.status_code != 200:
                return None

            status = response.json().get("status")

            if status == "ERROR":
                return None

            if status == "COMPLETE":
                break

            time.sleep(3)

        except requests.RequestException:
            return None

    else:

        return None


    try:

        response = requests.get(
            f"{FOLDSEEK_API}/result/{ticket_id}/0",
            timeout=60
        )

        if response.status_code != 200:
            return None

        data = response.json()

        hits = []

        for result in data.get("results", []):

            alignments = result.get(
                "alignments",
                []
            )

            # Handle unexpected API format
            if isinstance(alignments, dict):
                alignments = [alignments]

            if not isinstance(alignments, list):
                continue

            for hit in alignments:

                # Ignore invalid objects
                if not isinstance(hit, dict):
                    continue

                target = hit.get(
                    "target",
                    "Unknown"
                )

                hits.append({
                    "target": target,

                    "sequence_identity": hit.get(
                        "seqId",
                        "N/A"
                    ),

                    "e_value": hit.get(
                        "eval",
                        "N/A"
                    ),

                    "alignment_length": hit.get(
                        "alnLength",
                        "N/A"
                    ),

                    "score": hit.get(
                        "score",
                        "N/A"
                    )
                })

        return hits[:max_results]

    except (requests.RequestException, ValueError, TypeError):

        return None


def search_foldseek(
    structure_url,
    protein_id,
    max_results=5
):

    ticket_id = submit_structure(
        structure_url,
        protein_id
    )

    if not ticket_id:
        return None

    return get_foldseek_results(
        ticket_id,
        max_results
    )
