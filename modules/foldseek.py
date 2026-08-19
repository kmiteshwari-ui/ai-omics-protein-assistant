import requests
import tempfile
import os


def download_alphafold_pdb(protein_id):
    url = f"https://alphafold.ebi.ac.uk/files/AF-{protein_id}-F1-model_v6.pdb"

    response = requests.get(url, timeout=30)

    if response.status_code != 200:
        return None

    return response.text


def search_foldseek(protein_id):
    pdb_content = download_alphafold_pdb(protein_id)

    if not pdb_content:
        return None

    temp_file = None

    try:
        with tempfile.NamedTemporaryFile(
            mode="w",
            suffix=".pdb",
            delete=False
        ) as f:
            f.write(pdb_content)
            temp_file = f.name

        # Foldseek web API
        url = "https://search.foldseek.com/api/ticket"

        with open(temp_file, "rb") as pdb_file:

            files = {
                "q": pdb_file
            }

            data = {
                "database[]": "pdb100",
                "mode": "3diaa"
            }

            response = requests.post(
                url,
                files=files,
                data=data,
                timeout=60
            )

        if response.status_code != 200:
            return None

        return response.json()

    except requests.RequestException:
        return None

    finally:
        if temp_file and os.path.exists(temp_file):
            os.remove(temp_file)
