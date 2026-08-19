import streamlit as st

from modules.uniprot import get_protein_info
from modules.alphafold import get_alphafold_info


st.set_page_config(
    page_title="AI Omics & Protein Assistant",
    page_icon="🧬",
    layout="wide"
)


# -----------------------------
# Header
# -----------------------------

st.title("🧬 AI Omics & Protein Intelligence Assistant")

st.write(
    "An AI-assisted platform for protein analysis, "
    "functional annotation, structural analysis, "
    "and biomarker discovery."
)

st.divider()


# -----------------------------
# Protein Input
# -----------------------------

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

            st.error(
                "Protein ID not found. "
                "Please check the UniProt / TrEMBL ID."
            )

        else:

            st.success(
                "Protein information retrieved successfully!"
            )


            # -----------------------------
            # Protein Information
            # -----------------------------

            st.subheader("🧬 Protein Information")

            col1, col2 = st.columns(2)

            with col1:

                st.write(
                    "**Protein ID:**",
                    protein["protein_id"]
                )

                st.write(
                    "**Protein Name:**",
                    protein["protein_name"]
                )

                st.write(
                    "**Gene Name:**",
                    protein["gene_name"]
                )


            with col2:

                st.write(
                    "**Organism:**",
                    protein["organism"]
                )

                st.write(
                    "**Length:**",
                    protein["length"],
                    "amino acids"
                )


            # -----------------------------
            # Function
            # -----------------------------

            st.subheader("🔬 Functional Annotation")

            st.write(
                "**Function:**",
                protein["function"]
            )


            # -----------------------------
            # GO Terms
            # -----------------------------

            st.write("**GO Terms:**")

            go_terms = protein["go_terms"]

            if go_terms and go_terms[0] != "Not available":

                for go in go_terms:
                    st.write("•", go)

            else:

                st.write("Not available")


            st.divider()


            # -----------------------------
            # AlphaFold
            # -----------------------------

            st.subheader("🧊 AlphaFold Structure")

            with st.spinner(
                "Fetching AlphaFold information..."
            ):

                alphafold = get_alphafold_info(
                    protein_id
                )


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
                    "AlphaFold information not available "
                    "for this protein."
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
