import streamlit as st
import pandas as pd

from modules.uniprot import get_protein_info
from modules.alphafold import get_alphafold_info
from modules.structure import get_pdb_structure
from modules.foldseek import search_foldseek
from modules.hit_annotation import get_hit_annotation
from modules.biomarker import analyze_single_protein
from modules.ai_assistant import generate_protein_analysis
from modules.structure_viewer import show_structure


st.set_page_config(
    page_title="AI Omics & Protein Intelligence Assistant",
    page_icon="🧬",
    layout="wide"
)


# ==========================================
# SESSION STATE
# ==========================================

defaults = {
    "protein": None,
    "structure": None,
    "alphafold": None,
    "foldseek_results": None,
    "annotated_hits": None,
    "biomarker_result": None,
    "ai_analysis": None,
    "protein_id": None
}

for key, value in defaults.items():
    if key not in st.session_state:
        st.session_state[key] = value


# ==========================================
# HEADER
# ==========================================

st.title(
    "🧬 AI Omics & Protein Intelligence Assistant"
)

st.write(
    "An AI-assisted platform for protein analysis, "
    "structural analysis, functional annotation, "
    "and biomarker investigation."
)


# ==========================================
# SIDEBAR
# ==========================================

st.sidebar.title("Analysis Modules")
st.sidebar.write("🧬 Protein Information")
st.sidebar.write("🧊 Structure Analysis")
st.sidebar.write("🔎 Foldseek Similarity")
st.sidebar.write("📊 Biomarker Analysis")
st.sidebar.write("🤖 AI Research Assistant")


# ==========================================
# PROTEIN SEARCH
# ==========================================

st.header("🧬 Protein Analysis")

protein_id = st.text_input(
    "Enter UniProt / TrEMBL Protein ID",
    placeholder="Example: P00722"
)


if st.button("🔍 Analyze Protein"):

    if not protein_id.strip():
        st.warning("Please enter a protein ID.")
        st.stop()

    protein_id = protein_id.strip().upper()

    st.session_state.protein_id = protein_id
    st.session_state.ai_analysis = None
    st.session_state.biomarker_result = None

    # --------------------------------------
    # UniProt
    # --------------------------------------

    with st.spinner(
        "Fetching UniProt information..."
    ):
        protein = get_protein_info(protein_id)

    if protein is None:
        st.error("Protein ID not found.")
        st.session_state.protein = None
        st.stop()

    st.session_state.protein = protein

    # --------------------------------------
    # Structure
    # --------------------------------------

    with st.spinner(
        "Searching for experimental structure..."
    ):
        pdb_structure = get_pdb_structure(
            protein_id
        )

    if pdb_structure:

        st.session_state.structure = pdb_structure
        st.session_state.alphafold = None

    else:

        with st.spinner(
            "No PDB structure found. "
            "Fetching AlphaFold prediction..."
        ):
            alphafold = get_alphafold_info(
                protein_id
            )

        st.session_state.alphafold = alphafold

        if alphafold:

            st.session_state.structure = {
                "source": "AlphaFold",
                "pdb_id": None,
                "structure_url": alphafold.get(
                    "pdb_url"
                ),
                "page_url": None
            }

        else:
            st.session_state.structure = None

    # --------------------------------------
    # Foldseek
    # --------------------------------------

    st.session_state.foldseek_results = None
    st.session_state.annotated_hits = None

    structure = st.session_state.structure

    if structure and structure.get("structure_url"):

        with st.spinner(
            "Searching structural similarities with Foldseek..."
        ):

            foldseek_results = search_foldseek(
                structure["structure_url"],
                protein_id,
                max_results=5
            )

        st.session_state.foldseek_results = (
            foldseek_results
        )

        if foldseek_results:

            annotated_hits = []

            for hit in foldseek_results:

                annotation = get_hit_annotation(
                    hit.get("target")
                )

                annotated_hits.append({
                    **hit,
                    **annotation
                })

            st.session_state.annotated_hits = (
                annotated_hits
            )

    st.success(
        "Protein analysis completed!"
    )


# ==========================================
# LOAD RESULTS
# ==========================================

protein = st.session_state.protein
structure = st.session_state.structure
alphafold = st.session_state.alphafold
annotated_hits = st.session_state.annotated_hits


# ==========================================
# PROTEIN INFORMATION
# ==========================================

if protein:

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

    if protein["function"] != "Not available":

        st.success(
            "Curated UniProt functional annotation"
        )

        st.write(
            protein["function"]
        )

    else:

        st.info(
            "No curated functional annotation "
            "is currently available."
        )

    st.write("**GO Terms:**")

    for go in protein["go_terms"]:
        st.write("•", go)


    st.divider()


    # ======================================
    # STRUCTURE
    # ======================================

    st.subheader("🧊 Structure Analysis")

    if structure:

        if structure.get("source") == "PDB":

            st.success(
                "Experimental PDB structure found."
            )

            st.write(
                "**PDB ID:**",
                structure.get("pdb_id")
            )

            if structure.get("page_url"):
                st.link_button(
                    "🔗 Open PDB Entry",
                    structure["page_url"]
                )


        elif structure.get("source") == "AlphaFold":

            st.info(
                "No suitable experimental PDB structure "
                "was found. Using AlphaFold prediction."
            )

            if alphafold:

                st.write(
                    "**pLDDT Score:**",
                    alphafold.get(
                        "plddt",
                        "N/A"
                    )
                )


        # ----------------------------------
        # 3D Viewer
        # ----------------------------------

        if structure.get("structure_url"):

            st.subheader(
                "🧊 Interactive 3D Structure"
            )

            show_structure(
                structure["structure_url"]
            )

    else:

        st.warning(
            "No experimental or predicted structure "
            "was available."
        )


    st.divider()


    # ======================================
    # FOLDSEEK
    # ======================================

    st.subheader(
        "🔎 Structural Similarity — Foldseek"
    )

    if annotated_hits:

        st.success(
            f"Found {len(annotated_hits)} "
            "structural hits."
        )

        for i, hit in enumerate(
            annotated_hits,
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

            st.write(
                "**Hit UniProt ID:**",
                hit.get(
                    "uniprot_id",
                    "Not available"
                )
            )

            st.write(
                "**Hit Protein:**",
                hit.get(
                    "protein_name",
                    "Not available"
                )
            )

            st.write(
                "**Hit Organism:**",
                hit.get(
                    "organism",
                    "Not available"
                )
            )

            st.write(
                "**Expected Function:**",
                hit.get(
                    "function",
                    "Not available"
                )
            )

    else:

        st.warning(
            "No Foldseek results available."
        )


# ==========================================
# BIOMARKER ANALYSIS
# ==========================================

st.divider()

st.header("📊 Biomarker Evidence")

st.write(
    "Upload expression data and the application "
    "will evaluate the specific protein searched above."
)

uploaded_file = st.file_uploader(
    "Upload expression CSV",
    type=["csv"]
)


if uploaded_file:

    if not protein:

        st.warning(
            "Analyze a protein first."
        )

    else:

        try:

            df = pd.read_csv(
                uploaded_file
            )

            st.subheader(
                "Uploaded Expression Data"
            )

            st.dataframe(
                df,
                use_container_width=True
            )

            target_gene = protein.get(
                "gene_name"
            )

            if not target_gene or target_gene == "Not available":

                st.warning(
                    "A gene name was not available "
                    "for this protein."
                )

            else:

                st.info(
                    f"Checking biomarker evidence for "
                    f"**{target_gene}**."
                )

                biomarker_result = (
                    analyze_single_protein(
                        df,
                        target_gene
                    )
                )

                st.session_state.biomarker_result = (
                    biomarker_result
                )

                if biomarker_result is None:

                    st.warning(
                        f"{target_gene} was not found in "
                        "the uploaded dataset, or there "
                        "were insufficient samples."
                    )

                else:

                    st.subheader(
                        "🧪 Protein-specific Biomarker Evidence"
                    )

                    c1, c2, c3 = st.columns(3)

                    with c1:
                        st.metric(
                            "Fold Change",
                            f"{biomarker_result['fold_change']:.2f}"
                        )

                    with c2:
                        st.metric(
                            "Log₂ Fold Change",
                            f"{biomarker_result['log2_fold_change']:.2f}"
                        )

                    with c3:
                        st.metric(
                            "P-value",
                            f"{biomarker_result['p_value']:.4f}"
                        )

                    if biomarker_result[
                        "potential_biomarker"
                    ]:

                        st.success(
                            f"**{target_gene}** shows preliminary "
                            "evidence consistent with a potential "
                            "biomarker candidate."
                        )

                    else:

                        st.info(
                            f"**{target_gene}** does not meet "
                            "the current preliminary biomarker "
                            "criteria."
                        )


# ==========================================
# AI RESEARCH ASSISTANT
# ==========================================

st.divider()

st.header(
    "🤖 AI Research Assistant"
)

st.write(
    "Generate an integrated interpretation using "
    "protein, structural, Foldseek, and biomarker evidence."
)


if protein:

    if st.button(
        "🧠 Generate AI Analysis"
    ):

        with st.spinner(
            "Generating research interpretation..."
        ):

            st.session_state.ai_analysis = (
                generate_protein_analysis(
                    protein=protein,
                    alphafold=alphafold,
                    foldseek_results=annotated_hits,
                    biomarker_results=(
                        st.session_state.biomarker_result
                    )
                )
            )


    if st.session_state.ai_analysis:

        st.markdown(
            st.session_state.ai_analysis
        )

else:

    st.info(
        "Analyze a protein first to use "
        "the AI Research Assistant."
    )
