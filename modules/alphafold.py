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

        pdb_url = result.get("pdbUrl")

        # The AlphaFold prediction metadata endpoint does not
        # return a single summary pLDDT score. Per-residue pLDDT
        # values are stored in the B-factor column of the PDB
        # file, so we download the structure and average the
        # C-alpha atom B-factors to get a representative score.
        plddt = _get_average_plddt(pdb_url) if pdb_url else None

        return {
            "source": "AlphaFold",
            "protein_id": protein_id,
            "model_url": result.get("cifUrl"),
            "pdb_url": pdb_url,
            "plddt": plddt,
            "model_entity_id": result.get(
                "modelEntityId"
            )
        }

    except requests.RequestException:
        return None


def _get_average_plddt(pdb_url):
    """
    Download the AlphaFold PDB file and compute the mean
    per-residue pLDDT score from the B-factor column of the
    C-alpha (CA) atoms.
    """

    try:
        response = requests.get(pdb_url, timeout=30)

        if response.status_code != 200:
            return None

        scores = []

        for line in response.text.splitlines():

            # Standard PDB ATOM record layout:
            # columns 13-16 -> atom name, columns 61-66 -> B-factor
            if line.startswith("ATOM") and line[12:16].strip() == "CA":

                try:
                    b_factor = float(line[60:66])
                    scores.append(b_factor)
                except ValueError:
                    continue

        if not scores:
            return None

        return round(sum(scores) / len(scores), 2)

    except requests.RequestException:
        return None
