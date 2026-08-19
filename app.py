import streamlit as st
import pandas as pd
import numpy as np

from modules.uniprot import get_protein_info
from modules.alphafold import get_alphafold_info
from modules.foldseek import search_foldseek
from modules.biomarker import analyze_biomarkers
from modules.ai_assistant import generate_protein_analysis


st.set_page_config(
    page_title="AI Omics & Protein Assistant",
    page_icon="🧬",
    layout="wide"
)


# ==========================================
# SESSION STATE
# ==========================================

if "protein" not in st.session_state:
    st.session_state.protein = None

if "alphafold" not in st.session_state:
    st.session_state.alphafold = None

if "foldseek_results" not in st.session_state:
    st.session_state.foldseek_results = None

if "ai_analysis" not in st.session_state:
    st.session_state.ai_analysis = None

if "biomarker_results" not in st.session_state:
    st.session_state.biomarker_results = None


# ==========================================
# HEADER
# ==========================================

st.title("🧬 AI Omics & Protein Intelligence Assistant")

st.write(
    "An AI-assisted platform for protein analysis, "
    "structural analysis, functional annotation, "
    "and biomarker discovery."
)


# ==========================================
# SIDEBAR
# ==========================================

st.sidebar.title("Analysis Modules")
st.sidebar.write("🧬 Protein Information")
st.sidebar.write("🧊 AlphaFold Structure")
st.sidebar.write("🔎 Foldseek Similarity")
st.sidebar.write("📊 Biomarker Analysis")
st.sidebar.write("🤖 AI Research Assistant")


# ==========================================
# PROTEIN ANALYSIS
# ==========================================

st.header("🧬 Protein Analysis")

protein_id = st.text_input(
    "Enter UniProt / TrEMBL Protein ID",
    placeholder="Example: P00722"
)


if st.button("🔍 Analyze Protein"):

    if not protein_id:

        st.warning("Please enter a protein ID.")

    else:

        protein_id = protein_id.strip().upper()

        st.session_state.ai_analysis = None

        with st.spinner("Fetching UniProt information..."):

            protein = get_protein_info(protein_id)

        if protein is None:

            st.error("Protein ID not found.")
            st.session_state.protein = None

        else:

            st.session_state.protein = protein

            with st.spinner(
                "Fetching AlphaFold information..."
            ):

                st.session_state.alphafold = (
                    get_alphafold_info(protein_id)
                )

            with st.spinner(
                "Searching structural databases with Foldseek..."
            ):

                st.session_state.foldseek_results = (
                    search_foldseek(
                        protein_id,
                        max_results=5
                    )
                )

            st.success(
                "Protein analysis completed!"
            )


# ==========================================
# DISPLAY PROTEIN RESULTS
# ==========================================

protein = st.session_state.protein
alphafold = st.session_state.alphafold
foldseek_results = st.session_state.foldseek_results


if protein:

    # --------------------------------------
    # Protein Information
    # --------------------------------------

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


    # --------------------------------------
    # Functional Annotation
    # --------------------------------------

    st.subheader("🔬 Functional Annotation")

    st.write(
        "**Function:**",
        protein["function"]
    )

    st.write("**GO Terms:**")

    for go in protein["go_terms"]:
        st.write("•", go)


    st.divider()


    # --------------------------------------
    # AlphaFold
    # --------------------------------------

    st.subheader("🧊 AlphaFold Structure")

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


    # --------------------------------------
    # Foldseek
    # --------------------------------------

    st.subheader(
        "🔎 Structural Similarity — Foldseek"
    )

    if foldseek_results:

        st.success(
            f"Found {len(foldseek_results)} "
            "structural hits."
        )

        for i, hit in enumerate(
            foldseek_results,
            start=1
        ):

            st.markdown(
                f"### Hit {i}: "
                f"{hit.get('target', 'Unknown')}"
            )

            c1, c2, c3 = st.columns(3)

            with c1:

                st.write(
                    "**Sequence Identity:**",
                    hit.get(
                        "sequence_identity",
                        "N/A"
                    )
                )

            with c2:

                st.write(
                    "**E-value:**",
                    hit.get(
                        "e_value",
                        "N/A"
                    )
                )

            with c3:

                st.write(
                    "**Alignment Length:**",
                    hit.get(
                        "alignment_length",
                        "N/A"
                    )
                )

    else:

        st.warning(
            "No Foldseek results returned."
        )


# ==========================================
# BIOMARKER ANALYSIS
# ==========================================

st.divider()

st.header("📊 Biomarker Discovery")

st.write(
    "Upload an expression dataset containing "
    "multiple Healthy and Disease samples."
)


uploaded_file = st.file_uploader(
    "Upload expression CSV",
    type=["csv"]
)


if uploaded_file:

    try:

        df = pd.read_csv(uploaded_file)

        st.subheader("Uploaded Dataset")

        st.dataframe(
            df,
            use_container_width=True
        )

        results = analyze_biomarkers(df)

        if results is None:

            st.error(
                "CSV must contain Gene plus at least "
                "two Healthy (H) and two Disease (D) samples."
            )

        else:

            st.session_state.biomarker_results = results

            st.subheader(
                "🧪 Biomarker Candidates"
            )

            st.dataframe(
                results,
                use_container_width=True
            )


            # --------------------------------------
            # Top Candidates
            # --------------------------------------

            st.subheader("🏆 Top Candidates")

            for _, row in results.head(5).iterrows():

                st.write(
                    f"**{row['Gene']}** — "
                    f"Fold Change: "
                    f"{row['Fold Change']:.2f} | "
                    f"Adjusted P-value: "
                    f"{row['Adjusted P-value']:.4f}"
                )


            # --------------------------------------
            # Volcano Plot
            # --------------------------------------

            st.subheader("📊 Volcano Plot")

            plot_data = results.copy()

            plot_data[
                "-log10 Adjusted P-value"
            ] = -np.log10(
                plot_data["Adjusted P-value"] + 1e-300
            )

            st.scatter_chart(
                plot_data,
                x="Log2 Fold Change",
                y="-log10 Adjusted P-value"
            )


    except Exception as e:

        st.error(
            f"Error processing file: {e}"
        )


# ==========================================
# AI RESEARCH ASSISTANT
# ==========================================

st.divider()

st.header("🤖 AI Research Assistant")

st.write(
    "Generate an integrated interpretation using "
    "protein, structural, functional, and biomarker evidence."
)


if protein:

    if st.button("🧠 Generate AI Analysis"):

        with st.spinner(
            "Generating integrated research analysis..."
        ):

            st.session_state.ai_analysis = (
                generate_protein_analysis(
                    protein=protein,
                    alphafold=alphafold,
                    foldseek_results=foldseek_results,
                    biomarker_results=(
                        st.session_state.biomarker_results
                    )
                )
            )


    if st.session_state.ai_analysis:

        st.markdown(
            st.session_state.ai_analysis
        )

else:

    st.info(
        "Analyze a protein first to use the AI Research Assistant."
    )
