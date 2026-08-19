import requests
import time


FOLDSEEK_API = "https://search.foldseek.com/api"


def submit_structure(structure_url, protein_id):
    """Download the structure and submit it to Foldseek."""

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

        result = response.json()

        return result.get("id")

    except requests.RequestException:
        return None


def get_foldseek_results(ticket_id, max_results=5):
    """Poll Foldseek and retrieve the results."""

    for _ in range(40):

        try:
            status_response = requests.get(
                f"{FOLDSEEK_API}/ticket/{ticket_id}",
                timeout=30
            )

            if status_response.status_code != 200:
                return None

            status_data = status_response.json()

            status = status_data.get("status")

            if status == "ERROR":
                return None

            if status == "COMPLETE":
                break

            time.sleep(3)

        except requests.RequestException:
            return None

    else:
        return None


    # Get first result set
    try:

        result_response = requests.get(
            f"{FOLDSEEK_API}/result/{ticket_id}/0",
            timeout=60
        )

        if result_response.status_code != 200:
            return None

        data = result_response.json()

    except (requests.RequestException, ValueError):
        return None


    hits = []


    # ======================================
    # Parse Foldseek result
    # ======================================

    for result_group in data.get("results", []):

        alignments = result_group.get(
            "alignments",
            []
        )

        if not isinstance(alignments, list):
            continue


        for alignment in alignments:

            if not isinstance(alignment, dict):
                continue


            # Some Foldseek responses contain
            # the actual hit information inside
            # the "aln" list.

            nested = alignment.get("aln")


            if isinstance(nested, list) and nested:

                for hit in nested:

                    if not isinstance(hit, dict):
                        continue

                    hits.append(
                        extract_hit(hit)
                    )

            else:

                hits.append(
                    extract_hit(alignment)
                )


    # Remove empty/duplicate targets
    unique_hits = []

    seen = set()

    for hit in hits:

        target = hit.get(
            "target",
            "Unknown"
        )

        if target not in seen:

            seen.add(target)
            unique_hits.append(hit)


    return unique_hits[:max_results]


def extract_hit(hit):
    """Safely extract useful Foldseek fields."""

    return {

        "target": hit.get(
            "target",
            "Unknown"
        ),

        "sequence_identity": hit.get(
            "fident",
            hit.get(
                "seqId",
                "N/A"
            )
        ),

        "e_value": hit.get(
            "evalue",
            hit.get(
                "eval",
                "N/A"
            )
        ),

        "alignment_length": hit.get(
            "alnlen",
            hit.get(
                "alnLength",
                "N/A"
            )
        ),

        "bit_score": hit.get(
            "bits",
            "N/A"
        ),

        # TM-score fields
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

        # Structural confidence
        "lddt": hit.get(
            "lddt",
            "N/A"
        ),

        # Homology probability
        "probability": hit.get(
            "prob",
            "N/A"
        )
    }


def search_foldseek(
    structure_url,
    protein_id,
    max_results=5
):
    """Complete Foldseek search pipeline."""

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
