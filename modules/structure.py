import requests


def get_pdb_structure(uniprot_id):
    """
    Find an experimental PDB structure mapped to a UniProt ID.
    Returns the best available PDB entry or None.
    """

    url = "https://search.rcsb.org/rcsbsearch/v2/query"

    query = {
        "query": {
            "type": "terminal",
            "service": "text",
            "parameters": {
                "attribute": "rcsb_polymer_entity_container_identifiers.reference_sequence_identifiers.database_accession",
                "operator": "exact_match",
                "value": uniprot_id
            }
        },
        "return_type": "entry",
        "request_options": {
            "paginate": {
                "start": 0,
                "rows": 10
            }
        }
    }

    try:
        response = requests.post(
            url,
            json=query,
            timeout=30
        )

        if response.status_code != 200:
            return None

        data = response.json()

        results = data.get("result_set", [])

        if not results:
            return None

        pdb_id = results[0].get("identifier")

        if not pdb_id:
            return None

        return {
            "source": "PDB",
            "pdb_id": pdb_id,
            "structure_url": (
                f"https://files.rcsb.org/download/"
                f"{pdb_id}.pdb"
            ),
            "page_url": (
                f"https://www.rcsb.org/structure/"
                f"{pdb_id}"
            )
        }

    except requests.RequestException:
        return None
