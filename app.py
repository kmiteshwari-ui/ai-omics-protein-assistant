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


# ==========================================
# PAGE
# ==========================================

st.set_page_config(
    page_title="AI Omics & Protein Assistant",
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
    "ai_analysis": None
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
    "and biomarker discovery."
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
# PROTEIN INPUT
# ==========================================

st.header("🧬 Protein Analysis")

protein_id = st.text_input(
    "Enter UniProt / TrEMBL Protein ID",
    placeholder="Example: P00722"
)


if st.button("🔍 Analyze Protein"):

    if not protein_id:

        st.warning(
            "Please enter a UniProt / TrEMBL ID."
        )

        st.stop()

    protein_id = protein_id.strip().upper()

    # Reset previous results

    st.session_state.structure = None
    st.session_state.alphafold = None
    st.session_state.foldseek_results = None
    st.session_state.annotated_hits = None
    st.session_state.ai_analysis = None
    st.session_state.biomarker_result = None

    # ======================================
    # UNIPROT
    # ======================================

    with st.spinner(
        "Fetching UniProt information..."
    ):

        protein, error = get_protein_info(
            protein_id
        )

    if protein is None:

        st.error(
            error or "Protein ID not found."
        )

        st.session_state.protein = None

        st.stop()

    st.session_state.protein = protein


    # ======================================
    # STRUCTURE: PDB FIRST
    # ======================================

    with st.spinner(
        "Searching for experimental PDB structure..."
    ):

        pdb_structure = get_pdb_structure(
            protein_id
        )

    if pdb_structure:

        st.session_state.structure = pdb_structure

    else:

        # ==================================
        # ALPHAFOLD FALLBACK
        # ==================================

        with st.spinner(
            "No suitable PDB structure found. "
            "Fetching AlphaFold prediction..."
        ):

            alphafold = get_alphafold_info(
                protein_id
            )

        if alphafold:

            st.session_state.alphafold = alphafold

            st.session_state.structure = {
                "source": "AlphaFold",
                "pdb_id": None,
                "structure_url": alphafold.get(
                    "pdb_url"
                ),
                "page_url": None
            }


    # ======================================
    # FOLDSEEK
    # ======================================

    structure = st.session_state.structure

    if structure and structure.get(
        "structure_url"
    ):

        with st.spinner(
            "Searching structural similarities "
            "with Foldseek..."
        ):

            try:

                foldseek_results = search_foldseek(
                    structure["structure_url"],
                    protein_id,
                    max_results=5
                )

            except Exception as e:

                st.warning(
                    f"Foldseek search failed: {e}"
                )

                foldseek_results = None

        if foldseek_results is None:

            st.info(
                "Foldseek returned no results. This can "
                "happen if the search server is busy, "
                "the structure could not be downloaded, "
                "or the search timed out."
            )

        st.session_state.foldseek_results = (
            foldseek_results
        )


        # ==================================
        # ANNOTATE FOLDSEEK HITS
        # ==================================

        if foldseek_results:

            annotated_hits = []

            for hit in foldseek_results:

                annotation = get_hit_annotation(
                    hit.get("target")
                )

                combined_hit = {
                    **hit,
                    **annotation
                }

                annotated_hits.append(
                    combined_hit
                )

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

foldseek_results = (
    st.session_state.foldseek_results
)

annotated_hits = (
    st.session_state.annotated_hits
)


# ==========================================
# PROTEIN INFORMATION
# ==========================================

if protein:

    st.subheader(
        "🧬 Protein Information"
    )

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

    st.subheader(
        "🔬 Functional Annotation"
    )

    function = protein["function"]

    if function != "Not available":

        st.success(
            "Curated UniProt functional annotation"
        )

        st.write(
            function
        )

    else:

        st.info(
            "No curated functional annotation "
            "is currently available."
        )


    # ======================================
    # GO
    # ======================================

    st.write(
        "**GO Terms:**"
    )

    for go in protein["go_terms"]:

        st.write(
            "•",
            go
        )


    st.divider()


    # ======================================
    # STRUCTURE
    # ======================================

    st.subheader(
        "🧊 Structure Analysis"
    )

    if structure:

        source = structure.get(
            "source"
        )

        if source == "PDB":

            st.success(
                "Experimental structure found in PDB."
            )

            st.write(
                "**PDB ID:**",
                structure["pdb_id"]
            )

            if structure.get("page_url"):

                st.link_button(
                    "🔗 Open PDB Entry",
                    structure["page_url"]
                )


        elif source == "AlphaFold":

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

                st.caption(
                    "pLDDT represents AlphaFold's "
                    "predicted local structural confidence."
                )


        # ==================================
        # 3D VIEWER
        # ==================================

        if structure.get(
            "structure_url"
        ):

            st.subheader(
                "🧊 Interactive 3D Structure"
            )

            show_structure(
                structure["structure_url"]
            )


    else:

        st.warning(
            "No experimental or predicted "
            "structure was available."
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

            target = hit.get(
                "target",
                "Unknown"
            )

            st.markdown(
                f"### Hit {i}: {target}"
            )


            # ==================================
            # FOLDSEEK METRICS — ROW 1
            # ==================================

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


            # ==================================
            # FOLDSEEK METRICS — ROW 2
            # ==================================

            c4, c5, c6 = st.columns(3)

            with c4:

                st.write(
                    "**TM-score:**",
                    hit.get(
                        "tm_score",
                        "N/A"
                    )
                )

            with c5:

                st.write(
                    "**LDDT:**",
                    hit.get(
                        "lddt",
                        "N/A"
                    )
                )

            with c6:

                st.write(
                    "**Homology Probability:**",
                    hit.get(
                        "probability",
                        "N/A"
                    )
                )


            # ==================================
            # HIT ANNOTATION
            # ==================================

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


            hit_function = hit.get(
                "function",
                "Not available"
            )

            if hit_function != "Not available":

                st.write(
                    "**Expected Function:**",
                    hit_function
                )

            else:

                st.write(
                    "**Expected Function:**",
                    "Not available"
                )


    elif foldseek_results:

        st.warning(
            "Foldseek hits were found, but their "
            "functional annotations could not be retrieved."
        )


    else:

        st.warning(
            "No Foldseek results returned."
        )


    st.divider()


# ==========================================
# BIOMARKER ANALYSIS — for the searched protein only
# ==========================================

st.header(
    "📊 Biomarker Evidence"
)

if protein is None:

    st.info(
        "Analyze a protein above first — biomarker "
        "evidence will then be matched to its gene "
        "automatically."
    )

else:

    target_gene = protein.get("gene_name")

    st.write(
        f"Looking for expression evidence for "
        f"**{target_gene}** "
        f"({protein['protein_name']})."
    )

    uploaded_file = st.file_uploader(
        "Upload expression CSV "
        "(Gene, Healthy replicate columns starting "
        "with H, Disease replicate columns starting "
        "with D)",
        type=["csv"]
    )

    if uploaded_file:

        try:

            df = pd.read_csv(
                uploaded_file
            )

            if target_gene in (None, "Not available"):

                st.warning(
                    "No gene name is available for "
                    f"{protein['protein_name']} "
                    f"({protein['protein_id']}), so it "
                    "can't be matched against this dataset."
                )

                st.session_state.biomarker_result = None

            else:

                biomarker_result = analyze_single_protein(
                    df, target_gene
                )

                st.session_state.biomarker_result = (
                    biomarker_result
                )

                if biomarker_result is None:

                    st.warning(
                        f"**{target_gene}** was not found in "
                        "the uploaded dataset, or the CSV "
                        "isn't in the expected format (Gene "
                        "plus at least two Healthy (H) and "
                        "two Disease (D) columns)."
                    )

                else:

                    candidate = biomarker_result.get(
                        "Candidate"
                    )

                    c1, c2, c3 = st.columns(3)

                    with c1:
                        st.metric(
                            "Healthy Mean",
                            f"{biomarker_result['Healthy Mean']:.2f}"
                        )

                    with c2:
                        st.metric(
                            "Disease Mean",
                            f"{biomarker_result['Disease Mean']:.2f}"
                        )

                    with c3:
                        st.metric(
                            "Fold Change",
                            f"{biomarker_result['Fold Change']:.2f}"
                        )

                    c4, c5 = st.columns(2)

                    with c4:
                        st.metric(
                            "Log2 Fold Change",
                            f"{biomarker_result['Log2 Fold Change']:.2f}"
                        )

                    with c5:
                        st.metric(
                            "Adjusted P-value",
                            f"{biomarker_result['Adjusted P-value']:.4f}"
                        )

                    if candidate == "Potential Candidate":

                        st.success(
                            f"**{target_gene}** is flagged as a "
                            "**potential biomarker candidate** "
                            "based on this dataset."
                        )

                    else:

                        st.info(
                            f"**{target_gene}** does not meet the "
                            "fold-change / significance thresholds "
                            "in this dataset."
                        )

        except Exception as e:

            st.error(
                f"Error processing file: {e}"
            )


# ==========================================
# AI RESEARCH ASSISTANT
# ==========================================

st.divider()

st.header(
    "🤖 AI Research Assistant"
)

st.write(
    "Generate an integrated interpretation "
    "using protein, structural, functional, "
    "Foldseek and biomarker evidence."
)


if protein:

    if st.button(
        "🧠 Generate AI Analysis"
    ):

        with st.spinner(
            "Generating integrated research analysis..."
        ):

            st.session_state.ai_analysis = (
                generate_protein_analysis(
                    protein=protein,
                    alphafold=alphafold,
                    foldseek_results=(
                        annotated_hits
                    ),
                    biomarker_result=(
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
