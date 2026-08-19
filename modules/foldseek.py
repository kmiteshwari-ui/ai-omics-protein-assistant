import requests


def search_foldseek(protein_id):
    url = "https://search.foldseek.com/api/search"

    params = {
        "query": protein_id,
        "database[]": "pdb100",
        "mode": "3diaa"
    }

    try:
        response = requests.get(url, params=params, timeout=30)

        if response.status_code != 200:
            return None

        return response.json()

    except requests.RequestException:
        return None
