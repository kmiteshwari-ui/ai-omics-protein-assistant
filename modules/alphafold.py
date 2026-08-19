import requests


def get_alphafold_info(protein_id):
    url = f"https://alphafold.ebi.ac.uk/api/prediction/{protein_id}"

    response = requests.get(url, timeout=15)

    if response.status_code != 200:
        return None

    data = response.json()

    if not data:
        return None

    result = data[0]

    return {
        "protein_id": protein_id,
        "model_url": result.get("cifUrl"),
        "pdb_url": result.get("pdbUrl"),
        "pae_image": result.get("paeImageUrl"),
        "plddt": result.get("plddt"),
    }
