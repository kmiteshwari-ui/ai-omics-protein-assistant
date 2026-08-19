import streamlit as st
import pandas as pd

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

        # Reset previous AI response
        st.session_state.ai_analysis = None

        # -------------------------
        # UniProt
        # -------------------------

        with st.spinner("Fetching UniProt information..."):

            protein = get_protein_info(protein_id)

        if protein is None:

            st.error("Protein ID not found.")

            st.session_state.protein = None

        else:

            st.session_state.protein = protein

            st.success(
                "Protein information retrieved!"
            )

            # -------------------------
            # AlphaFold
            # -------------------------

            with st.spinner(
                "Fetching AlphaFold information..."
            ):

                st.session_state.alphafold = (
                    get_alphafold_info(protein_id)
                )

            # -------------------------
            # Foldseek
            # -------------------------

            with st.spinner(
                "Searching structural databases with Foldseek..."
            ):

                st.session_state.foldseek_results = (
                    search_foldseek(
                        protein_id,
                        max_results=5
                    )
                )


# ==========================================
# DISPLAY PROTEIN RESULTS
# ==========================================

protein = st.session_state.protein
alphafold = st.session_state.alphafold
foldseek_results = st.session_state.foldseek_results


if protein:

    # ======================================
    # PROTEIN INFORMATION
    # ======================================

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


    # ======================================
    # FUNCTION
    # ======================================

    st.subheader("🔬 Functional Annotation")

    st.write(
        "**Function:**",
        protein["function"]
    )

    st.write("**GO Terms:**")

    for go in protein["go_terms"]:

        st.write("•", go)


    st.divider()


    # ======================================
    # ALPHAFOLD
    # ======================================

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


    # ======================================
    # FOLDSEEK
    # ======================================

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


    st.divider()


    # ======================================
    # AI ASSISTANT
    # ======================================

    st.subheader(
        "🤖 AI Research Assistant"
    )

    st.write(
        "Generate an interpretation using "
        "the protein, structural and functional evidence."
    )


    if st.button("🧠 Generate AI Analysis"):

        with st.spinner(
            "Generating research interpretation..."
        ):

            st.session_state.ai_analysis = (
                generate_protein_analysis(
                    protein,
                    alphafold,
                    foldseek_results
                )
            )


    if st.session_state.ai_analysis:

        st.markdown(
            st.session_state.ai_analysis
        )


# ==========================================
# BIOMARKER ANALYSIS
# ==========================================

st.divider()

st.header("📊 Biomarker Discovery")

st.write(
    "Upload an expression dataset containing "
    "Gene, Healthy and Disease columns."
)


uploaded_file = st.file_uploader(
    "Upload expression CSV",
    type=["csv"]
)


if uploaded_file:

    try:

        df = pd.read_csv(
            uploaded_file
        )

        st.subheader(
            "Uploaded Dataset"
        )

        st.dataframe(
            df,
            use_container_width=True
        )

        results = analyze_biomarkers(
            df
        )

        if results is None:

            st.error(
                "CSV must contain: "
                "Gene, Healthy, Disease"
            )

        else:

            st.subheader(
                "🧪 Biomarker Candidates"
            )

            st.dataframe(
                results,
                use_container_width=True
            )

            st.subheader(
                "🏆 Top Candidates"
            )

            for _, row in results.head(5).iterrows():

                st.write(
                    f"**{row['Gene']}** — "
                    f"Fold Change: "
                    f"{row['Fold Change']:.2f} | "
                    f"Score: "
                    f"{row['Biomarker Score']:.1f}"
                )

    except Exception as e:

        st.error(
            f"Error processing file: {e}"
        )
