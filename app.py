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

st.sidebar.title(
    "Analysis Modules"
)

st.sidebar.write(
    "🧬 Protein Information"
)

st.sidebar.write(
    "🧊 Structure Analysis"
)

st.sidebar.write(
    "🔎 Foldseek Similarity"
)

st.sidebar.write(
    "📊 Biomarker Analysis"
)

st.sidebar.write(
    "🤖 AI Research Assistant"
)


# ==========================================
# PROTEIN SEARCH
# ==========================================

st.header(
    "🧬 Protein Analysis"
)

protein_id = st.text_input(
    "Enter UniProt / TrEMBL Protein ID",
    placeholder="Example: P00722"
)


if st.button(
    "🔍 Analyze Protein"
):

    if not protein_id.strip():

        st.warning(
            "Please enter a protein ID."
        )

        st.stop()


    protein_id = (
        protein_id
        .strip()
        .upper()
    )


    # Save searched protein ID

    st.session_state.protein_id = (
        protein_id
    )


    # Reset old analysis

    st.session_state.protein = None

    st.session_state.structure = None

    st.session_state.alphafold = None

    st.session_state.foldseek_results = None

    st.session_state.annotated_hits = None

    st.session_state.biomarker_result = None

    st.session_state.ai_analysis = None


    # ======================================
    # UNIPROT
    # ======================================

    with st.spinner(
        "Fetching UniProt information..."
    ):

        protein = get_protein_info(
            protein_id
        )


    if protein is None:

        st.error(
            "Protein ID not found."
        )

        st.session_state.protein = None

        st.stop()


    st.session_state.protein = (
        protein
    )


    # ======================================
    # STRUCTURE
    # ======================================

    with st.spinner(
        "Searching for experimental structure..."
    ):

        pdb_structure = (
            get_pdb_structure(
                protein_id
            )
        )


    if pdb_structure:

        st.session_state.structure = (
            pdb_structure
        )

        st.session_state.alphafold = None


    else:

        with st.spinner(
            "No PDB structure found. "
            "Fetching AlphaFold prediction..."
        ):

            alphafold = (
                get_alphafold_info(
                    protein_id
                )
            )


        st.session_state.alphafold = (
            alphafold
        )


        if alphafold:

            st.session_state.structure = {

                "source": "AlphaFold",

                "pdb_id": None,

                "structure_url": (
                    alphafold.get(
                        "pdb_url"
                    )
                ),

                "page_url": None

            }

        else:

            st.session_state.structure = None


    # ======================================
    # FOLDSEEK
    # ======================================

    st.session_state.foldseek_results = None

    st.session_state.annotated_hits = None


    structure = (
        st.session_state.structure
    )


    if (
        structure
        and structure.get(
            "structure_url"
        )
    ):

        with st.spinner(
            "Searching structural similarities "
            "with Foldseek..."
        ):

            # IMPORTANT:
            # KEEP THIS EXACTLY AS REQUESTED

            foldseek_results = search_foldseek(
                structure["structure_url"],
                protein_id,
                max_results=5
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

                annotation = (
                    get_hit_annotation(
                        hit.get(
                            "target"
                        )
                    )
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

protein = (
    st.session_state.protein
)

structure = (
    st.session_state.structure
)

alphafold = (
    st.session_state.alphafold
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
            protein.get(
                "protein_id",
                "Not available"
            )
        )


        st.write(
            "**Protein Name:**",
            protein.get(
                "protein_name",
                "Not available"
            )
        )


        st.write(
            "**Gene Name:**",
            protein.get(
                "gene_name",
                "Not available"
            )
        )


    with col2:

        st.write(
            "**Organism:**",
            protein.get(
                "organism",
                "Not available"
            )
        )


        st.write(
            "**Length:**",
            protein.get(
                "length",
                "N/A"
            ),
            "amino acids"
        )


    # ======================================
    # FUNCTION
    # ======================================

    st.subheader(
        "🔬 Functional Annotation"
    )


    function = protein.get(
        "function",
        "Not available"
    )


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
    # GO TERMS
    # ======================================

    st.write(
        "**GO Terms:**"
    )


    for go in protein.get(
        "go_terms",
        []
    ):

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

        if structure.get(
            "source"
        ) == "PDB":

            st.success(
                "Experimental PDB structure found."
            )


            st.write(
                "**PDB ID:**",
                structure.get(
                    "pdb_id",
                    "N/A"
                )
            )


            if structure.get(
                "page_url"
            ):

                st.link_button(
                    "🔗 Open PDB Entry",
                    structure[
                        "page_url"
                    ]
                )


        elif structure.get(
            "source"
        ) == "AlphaFold":

            st.info(
                "No suitable experimental PDB "
                "structure was found. Using "
                "AlphaFold prediction."
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
                structure[
                    "structure_url"
                ]
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

            st.markdown(
                f"### Hit {i}: "
                f"{hit.get('target', 'Unknown')}"
            )


            # ==================================
            # ROW 1
            # ==================================

            c1, c2, c3 = (
                st.columns(3)
            )


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
            # ROW 2
            # ==================================

            c4, c5, c6 = (
                st.columns(3)
            )


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

st.header(
    "📊 Biomarker Evidence"
)


st.write(
    "Disease-associated expression evidence "
    "is automatically retrieved from "
    "EMBL-EBI Expression Atlas for the "
    "searched protein's gene."
)


if protein:

    target_gene = protein.get(
        "gene_name"
    )


    if (
        not target_gene
        or target_gene == "Not available"
    ):

        st.warning(
            "A gene name was not available "
            "for this protein."
        )


    else:

        st.info(
            f"Expression analysis target: "
            f"**{target_gene}**"
        )


        # ==================================
        # WEB EXPRESSION ANALYSIS
        # ==================================

        with st.spinner(
            "Querying EMBL-EBI Expression Atlas..."
        ):

            try:

                biomarker_result = (
                    analyze_single_protein(
                        target_gene
                    )
                )

            except Exception as e:

                biomarker_result = None

                st.error(
                    "Error retrieving expression "
                    f"evidence: {e}"
                )


        st.session_state.biomarker_result = (
            biomarker_result
        )


        # ==================================
        # NO RESULT
        # ==================================

        if biomarker_result is None:

            st.warning(
                f"No disease-associated expression "
                f"evidence was returned for "
                f"**{target_gene}**."
            )


        else:

            st.success(
                "Expression evidence retrieved "
                "from EMBL-EBI Expression Atlas."
            )


            # ==================================
            # BIOMARKER SUMMARY
            # ==================================

            st.subheader(
                "🧪 Protein-specific "
                "Biomarker Evidence"
            )


            c1, c2, c3 = (
                st.columns(3)
            )


            with c1:

                st.metric(
                    "Gene",
                    biomarker_result.get(
                        "gene",
                        target_gene
                    )
                )


            with c2:

                st.metric(
                    "Overall Direction",
                    biomarker_result.get(
                        "direction",
                        "N/A"
                    )
                )


            with c3:

                best_p = (
                    biomarker_result.get(
                        "best_p_value"
                    )
                )


                if (
                    best_p is None
                    or pd.isna(best_p)
                ):

                    p_display = "N/A"

                else:

                    p_display = (
                        f"{best_p:.3g}"
                    )


                st.metric(
                    "Best P-value",
                    p_display
                )


            # ==================================
            # SUMMARY
            # ==================================

            st.write(
                biomarker_result.get(
                    "summary",
                    "No summary available."
                )
            )


            # ==================================
            # EXPRESSION EVIDENCE TABLE
            # ==================================

            evidence_df = (
                biomarker_result.get(
                    "evidence"
                )
            )


            if (
                evidence_df is not None
                and not evidence_df.empty
            ):

                st.subheader(
                    "📊 Disease-associated "
                    "Expression Evidence"
                )


                st.dataframe(
                    evidence_df,
                    use_container_width=True
                )


            # ==================================
            # BIOMARKER INTERPRETATION
            # ==================================

            if biomarker_result.get(
                "potential_biomarker",
                False
            ):

                st.success(
                    f"**{target_gene}** has "
                    "preliminary disease-associated "
                    "expression evidence consistent "
                    "with potential biomarker relevance."
                )

            else:

                st.info(
                    f"**{target_gene}** has "
                    "disease-associated expression "
                    "evidence, but it does not meet "
                    "the current preliminary "
                    "biomarker criterion."
                )


            # ==================================
            # SOURCE
            # ==================================

            source_url = (
                biomarker_result.get(
                    "source_url"
                )
            )


            st.caption(
                "Source: EMBL-EBI Expression Atlas. "
                "Results represent curated differential "
                "expression evidence across Atlas "
                "experiments; they are not necessarily "
                "a single standardized healthy-vs-disease "
                "cohort."
            )


            if source_url:

                st.link_button(
                    "🔗 Open Expression Atlas",
                    source_url
                )


else:

    st.info(
        "Analyze a protein first to retrieve "
        "web-based biomarker evidence."
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
    "protein, structural, Foldseek, and biomarker "
    "evidence."
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

                    foldseek_results=(
                        annotated_hits
                    ),

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
