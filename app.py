import streamlit as st
from modules.uniprot import get_protein_info

st.set_page_config(
    page_title="AI Omics & Protein Assistant",
    page_icon="🧬",
    layout="wide"
)

st.title("🧬 AI Omics & Protein Intelligence Assistant")
st.write(
    "Analyze protein information and generate biological insights "
    "using AI-assisted bioinformatics."
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
        with st.spinner("Fetching protein information..."):
            protein = get_protein_info(protein_id.strip())

        if protein is None:
            st.error("Protein ID not found. Please check the ID.")
        else:
            st.success("Protein information retrieved successfully!")

            st.subheader("🧬 Protein Information")

            col1, col2 = st.columns(2)

            with col1:
                st.write("**Protein ID:**", protein["protein_id"])
                st.write("**Protein Name:**", protein["protein_name"])
                st.write("**Organism:**", protein["organism"])

            with col2:
                st.write("**Length:**", protein["length"], "amino acids")

            st.subheader("🔬 Function")
            st.write(protein["function"])

st.sidebar.title("Analysis Modules")
st.sidebar.write("🧬 Protein Information")
st.sidebar.write("🔬 Structure Analysis")
st.sidebar.write("🧪 Functional Annotation")
st.sidebar.write("📊 Biomarker Analysis")
st.sidebar.write("🤖 AI Research Assistant")
