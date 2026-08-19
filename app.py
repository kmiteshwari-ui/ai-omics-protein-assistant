import streamlit as st

from modules.uniprot import get_protein_info
from modules.alphafold import get_alphafold_info
from modules.foldseek import search_foldseek


st.set_page_config(
    page_title="AI Omics & Protein Assistant",
    page_icon="🧬",
    layout="wide"
)

st.title("🧬 AI Omics & Protein Intelligence Assistant")

st.write(
    "An AI-assisted platform for protein analysis, "
    "functional annotation, structural analysis, "
    "and biomarker discovery."
)

st.divider()

protein_id = st.text_input(
    "Enter UniProt / TrEMBL Protein ID",
    placeholder="Example: P00722"
)

if st.button("🔍 Analyze Protein"):

    if not protein_id:
        st.warning("Please enter a protein ID.")

    else:

        protein_id = protein_id.strip().upper()

        # -----------------------------
        # UniProt
        # -----------------------------

        with st.spinner("Fetching UniProt information..."):
            protein = get_protein_info(protein_id)

        if protein is None:
            st.error("Protein ID not found.")
            st.stop()

        st.success("Protein information retrieved successfully!")

        st.subheader("🧬 Protein Information")

        col1, col2 = st.columns(2)

        with col1:
            st.write("**Protein ID:**", protein["protein_id"])
            st.write("**Protein Name:**", protein["protein_name"])
            st.write("**Gene Name:**", protein["gene_name"])

        with col2:
            st.write("**Organism:**", protein["organism"])
            st.write("**Length:**", protein["length"], "amino acids")

        # -----------------------------
        # Function
        # -----------------------------

        st.subheader("🔬 Functional Annotation")

        st.write("**Function:**", protein["function"])

        st.write("**GO Terms:**")

        if protein["go_terms"]:
            for go in protein["go_terms"]:
                st.write("•", go)
        else:
            st.write("Not available")

        st.divider()

        # -----------------------------
        # AlphaFold
        # -----------------------------

        st.subheader("🧊 AlphaFold Structure")

        with st.spinner("Fetching AlphaFold information..."):
            alphafold = get_alphafold_info(protein_id)

        if alphafold:

            st.write(
                "**pLDDT Score:**",
                alphafold["plddt"]
            )

            if alphafold.get("pdb_url"):
                st.link_button(
                    "🔗 View AlphaFold Structure",
                    alphafold["pdb_url"]
                )

            if alphafold.get("pae_image"):
                st.image(
                    alphafold["pae_image"],
                    caption="AlphaFold Predicted Aligned Error"
                )

        else:
            st.warning(
                "AlphaFold information not available."
            )

        st.divider()

        # -----------------------------
        # Foldseek
        # -----------------------------

        st.subheader("🔎 Structural Similarity — Foldseek")

        with st.spinner(
            "Searching structural databases with Foldseek..."
        ):

            foldseek_results = search_foldseek(
                protein_id,
                max_results=5
            )

        if foldseek_results:

            st.success(
                f"Found {len(foldseek_results)} structural hits."
            )

            for i, hit in enumerate(
                foldseek_results,
                start=1
            ):

                st.markdown(
                    f"### Hit {i}: {hit.get('target', 'Unknown')}"
                )

                c1, c2, c3 = st.columns(3)

                with c1:
                    st.write(
                        "**Sequence Identity:**",
                        hit.get("sequence_identity", "N/A")
                    )

                with c2:
                    st.write(
                        "**E-value:**",
                        hit.get("e_value", "N/A")
                    )

                with c3:
                    st.write(
                        "**Alignment Length:**",
                        hit.get("alignment_length", "N/A")
                    )

        else:

            st.warning(
                "No Foldseek results were returned."
            )


# -----------------------------
# Sidebar
# -----------------------------

st.sidebar.title("Analysis Modules")

st.sidebar.write("🧬 Protein Information")
st.sidebar.write("🧊 AlphaFold Structure")
st.sidebar.write("🔬 Functional Annotation")
st.sidebar.write("🔎 Foldseek Similarity")
st.sidebar.write("📊 Biomarker Analysis")
st.sidebar.write("🤖 AI Research Assistant")
