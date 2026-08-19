import requests


def get_alphafold_info(protein_id):

    url = (
        f"https://alphafold.ebi.ac.uk/"
        f"api/prediction/{protein_id}"
    )

    try:
        response = requests.get(
            url,
            timeout=30
        )

        if response.status_code != 200:
            return None

        data = response.json()

        if not data:
            return None

        result = data[0]

        return {
            "source": "AlphaFold",
            "protein_id": protein_id,
            "model_url": result.get("cifUrl"),
            "pdb_url": result.get("pdbUrl"),
            "plddt": result.get("plddt"),
            "model_entity_id": result.get(
                "modelEntityId"
            )
        }

    except requests.RequestException:
        return None
