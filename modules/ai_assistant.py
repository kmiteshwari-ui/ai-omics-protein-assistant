import os
from openai import OpenAI


def generate_protein_analysis(protein, alphafold=None, foldseek_results=None):
    api_key = os.getenv("OPENAI_API_KEY")

    if not api_key:
        return "OpenAI API key is not configured."

    client = OpenAI(api_key=api_key)

    prompt = f"""
You are a bioinformatics research assistant.

Analyze the following protein information.

PROTEIN:
ID: {protein.get("protein_id")}
Name: {protein.get("protein_name")}
Gene: {protein.get("gene_name")}
Organism: {protein.get("organism")}
Length: {protein.get("length")}
Function: {protein.get("function")}
GO Terms: {protein.get("go_terms")}

ALPHAFOLD:
{alphafold}

FOLDSEEK STRUCTURAL HITS:
{foldseek_results}

Provide a concise research-oriented interpretation covering:

1. Protein function
2. Structural evidence
3. Functional/biological significance
4. What the Foldseek hits may suggest
5. Whether this protein could be interesting for biomarker research
6. Recommended next investigation

Do not claim that a protein is a clinically validated biomarker.
Clearly distinguish evidence from hypotheses.
"""

    try:
        response = client.responses.create(
            model="gpt-5.6-luna",
            input=prompt
        )

        return response.output_text

    except Exception as e:
        return f"AI analysis failed: {e}"
