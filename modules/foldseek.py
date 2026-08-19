import requests
import time


FOLDSEEK_API = "https://search.foldseek.com/api"


def download_structure(structure_url):
    try:
        response = requests.get(
            structure_url,
            timeout=30
        )

        if response.status_code == 200:
            return response.content

    except requests.RequestException:
        pass

    return None


def submit_foldseek(structure_url, protein_id):

    structure = download_structure(
        structure_url
    )

    if not structure:
        return None

    files = {
        "q": (
            f"{protein_id}.pdb",
            structure,
            "application/octet-stream"
        )
    }

    data = {
        "mode": "3diaa",
        "database[]": "pdb100"
    }

    try:

        response = requests.post(
            f"{FOLDSEEK_API}/ticket",
            files=files,
            data=data,
            timeout=60
        )

        if response.status_code != 200:
            return None

        result = response.json()

        return result.get("id")

    except requests.RequestException:
        return None


def wait_for_result(ticket):

    for _ in range(40):

        try:

            response = requests.get(
                f"{FOLDSEEK_API}/ticket/{ticket}",
                timeout=30
            )

            if response.status_code != 200:
                return None

            status = response.json()

            if status.get("status") == "COMPLETE":
                return True

            if status.get("status") == "ERROR":
                return False

            time.sleep(3)

        except requests.RequestException:
            return None

    return None


def get_results(ticket, max_results=5):

    try:

        response = requests.get(
            f"{FOLDSEEK_API}/result/{ticket}/0",
            timeout=60
        )

        if response.status_code != 200:
            return None

        data = response.json()

    except (requests.RequestException, ValueError):
        return None


    hits = []


    for result in data.get("results", []):

        alignments = result.get(
            "alignments",
            []
        )

        if isinstance(alignments, dict):
            alignments = [alignments]

        for hit in alignments:

            if not isinstance(hit, dict):
                continue

            hits.append({
                "target": hit.get(
                    "target",
                    "Unknown"
                ),

                "sequence_identity": hit.get(
                    "fident",
                    "N/A"
                ),

                "e_value": hit.get(
                    "evalue",
                    "N/A"
                ),

                "alignment_length": hit.get(
                    "alnlen",
                    "N/A"
                ),

                "tm_score": hit.get(
                    "alntmscore",
                    "N/A"
                ),

                "query_tm_score": hit.get(
                    "qtmscore",
                    "N/A"
                ),

                "target_tm_score": hit.get(
                    "ttmscore",
                    "N/A"
                ),

                "lddt": hit.get(
                    "lddt",
                    "N/A"
                ),

                "probability": hit.get(
                    "prob",
                    "N/A"
                )
            })


    return hits[:max_results]


def search_foldseek(
    structure_url,
    protein_id,
    max_results=5
):

    ticket = submit_foldseek(
        structure_url,
        protein_id
    )

    if not ticket:
        return None


    completed = wait_for_result(
        ticket
    )

    if completed is not True:
        return None


    return get_results(
        ticket,
        max_results
    )
