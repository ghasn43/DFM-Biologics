"""
Streamlit Page 1: Candidate Input
Input sequence, modality, targets, and constraints
"""

import streamlit as st
import json
from typing import Optional

st.set_page_config(page_title="Candidate Input", layout="wide")

st.markdown("# 📝 Candidate Input")
st.markdown("Define your construct and manufacturability constraints")

# Session state initialization
if "candidate_data" not in st.session_state:
    st.session_state.candidate_data = {
        "project_name": "",
        "modality": "IgG_like_bispecific",
        "targets": [],
        "expression_system": "mammalian",
        "sequence_type": "protein",
        "sequence": "",
        "notes": "",
    }

if "constraints_data" not in st.session_state:
    st.session_state.constraints_data = {
        "max_fragment_length": 500,
        "gc_min": 0.3,
        "gc_max": 0.7,
        "max_homopolymer": 6,
        "forbidden_motifs": [],
        "restriction_sites_to_avoid": [],
        "vendor_profile": "generic",
    }

# Left column: Candidate spec
col1, col2 = st.columns(2)

with col1:
    st.subheader("Project Specification")
    
    st.session_state.candidate_data["project_name"] = st.text_input(
        "Project Name",
        value=st.session_state.candidate_data["project_name"],
        placeholder="e.g., HER2-bispecific-v1"
    )
    
    st.session_state.candidate_data["modality"] = st.selectbox(
        "Construct Modality",
        ["IgG_like_bispecific", "VHH_bispecific", "Fab_scFv", "Fc_fusion"],
        index=["IgG_like_bispecific", "VHH_bispecific", "Fab_scFv", "Fc_fusion"].index(
            st.session_state.candidate_data["modality"]
        )
    )
    
    targets = st.multiselect(
        "Targets",
        ["HER2", "HER3", "EGFR", "PD-L1", "Other"],
        default=st.session_state.candidate_data["targets"] if st.session_state.candidate_data["targets"] else []
    )
    if "Other" in targets:
        custom_target = st.text_input("Enter custom target:")
        if custom_target:
            targets = [t for t in targets if t != "Other"] + [custom_target]
    st.session_state.candidate_data["targets"] = targets
    
    st.session_state.candidate_data["expression_system"] = st.selectbox(
        "Expression System",
        ["mammalian", "yeast", "ecoli", "cell_free"],
        index=["mammalian", "yeast", "ecoli", "cell_free"].index(
            st.session_state.candidate_data["expression_system"]
        )
    )
    
    st.session_state.candidate_data["sequence_type"] = st.selectbox(
        "Sequence Type",
        ["protein", "dna_cds"],
        index=["protein", "dna_cds"].index(
            st.session_state.candidate_data["sequence_type"]
        )
    )
    
    st.session_state.candidate_data["notes"] = st.text_area(
        "Design Notes (optional)",
        value=st.session_state.candidate_data["notes"],
        placeholder="e.g., Design rationale, special requirements",
        height=80
    )

with col2:
    st.subheader("Manufacturing Constraints")
    
    st.session_state.constraints_data["max_fragment_length"] = st.number_input(
        "Max Fragment Length (bp/aa)",
        min_value=50,
        max_value=5000,
        value=st.session_state.constraints_data["max_fragment_length"],
        step=50
    )
    
    col_gc1, col_gc2 = st.columns(2)
    with col_gc1:
        st.session_state.constraints_data["gc_min"] = st.slider(
            "Min GC Content",
            min_value=0.0,
            max_value=1.0,
            value=st.session_state.constraints_data["gc_min"],
            step=0.05,
            format="%.1f%%"
        )
    with col_gc2:
        st.session_state.constraints_data["gc_max"] = st.slider(
            "Max GC Content",
            min_value=0.0,
            max_value=1.0,
            value=st.session_state.constraints_data["gc_max"],
            step=0.05,
            format="%.1f%%"
        )
    
    st.session_state.constraints_data["max_homopolymer"] = st.number_input(
        "Max Homopolymer Length",
        min_value=3,
        max_value=15,
        value=st.session_state.constraints_data["max_homopolymer"],
        step=1
    )
    
    vendor_profile = st.selectbox(
        "Vendor Profile",
        ["generic", "twist_like", "idt_like"],
        index=["generic", "twist_like", "idt_like"].index(
            st.session_state.constraints_data["vendor_profile"]
        )
    )
    st.session_state.constraints_data["vendor_profile"] = vendor_profile
    
    st.markdown("**Forbidden Motifs** (comma-separated)")
    forbidden_input = st.text_input(
        "e.g., AAAA,GGGG",
        value=",".join(st.session_state.constraints_data["forbidden_motifs"]),
        placeholder="Leave blank for none"
    )
    st.session_state.constraints_data["forbidden_motifs"] = [
        m.strip().upper() for m in forbidden_input.split(",") if m.strip()
    ]
    
    st.markdown("**Restriction Sites to Avoid** (comma-separated)")
    sites_input = st.text_input(
        "e.g., EcoRI,BamHI",
        value=",".join(st.session_state.constraints_data["restriction_sites_to_avoid"]),
        placeholder="Leave blank for none"
    )
    st.session_state.constraints_data["restriction_sites_to_avoid"] = [
        s.strip() for s in sites_input.split(",") if s.strip()
    ]

# Sequence input (full width)
st.markdown("---")
st.subheader("Sequence")

sequence_input = st.text_area(
    "Paste protein or DNA sequence (FASTA format accepted)",
    value=st.session_state.candidate_data["sequence"],
    height=150,
    placeholder=">myseq\nMVHLTPEEKS...\nor\n>dna_seq\nATGCCG...",
)
st.session_state.candidate_data["sequence"] = sequence_input

# Validate
if st.session_state.candidate_data["sequence"]:
    from backend.core.utils import normalize_fasta, is_protein_sequence, is_dna_sequence
    
    normalized = normalize_fasta(st.session_state.candidate_data["sequence"])
    st.info(f"✅ Sequence length: {len(normalized)} {'aa' if is_protein_sequence(normalized) else 'bp'}")

# Action buttons
st.markdown("---")
col_btn1, col_btn2, col_btn3 = st.columns(3)

with col_btn1:
    if st.button("🔨 Generate Blueprint", use_container_width=True):
        if not st.session_state.candidate_data["project_name"]:
            st.error("Please enter a project name")
        elif not st.session_state.candidate_data["sequence"]:
            st.error("Please enter a sequence")
        else:
            try:
                from backend.core.checks_construct import ConstructChecker
                
                blueprint = ConstructChecker.generate_blueprint(
                    project_name=st.session_state.candidate_data["project_name"],
                    modality=st.session_state.candidate_data["modality"],
                    sequence=st.session_state.candidate_data["sequence"],
                    expression_system=st.session_state.candidate_data["expression_system"]
                )
                # Convert Pydantic model to dict for session storage
                st.session_state.blueprint_result = blueprint.model_dump()
                st.success("Blueprint generated! Go to **Construct Architecture** to view it.")
            except Exception as e:
                st.error(f"Error generating blueprint: {e}")

with col_btn2:
    if st.button("⚙️ Score Construct", use_container_width=True):
        if not st.session_state.candidate_data["project_name"]:
            st.error("Please enter a project name")
        elif not st.session_state.candidate_data["sequence"]:
            st.error("Please enter a sequence")
        else:
            try:
                from backend.core.scoring import ManufacturabilityScoringEngine
                from backend.core.models import CandidateSpec, ManufacturingConstraints
                
                # Create Pydantic models from session state
                candidate = CandidateSpec(**st.session_state.candidate_data)
                constraints = ManufacturingConstraints(**st.session_state.constraints_data)
                
                # Run scoring
                engine = ManufacturabilityScoringEngine()
                result = engine.score(candidate, constraints)
                
                # Convert to dict for session storage
                st.session_state.score_result = result.model_dump()
                st.success("Scoring complete! Go to **Manufacturability Report** to view results.")
            except Exception as e:
                st.error(f"Error during scoring: {e}")

with col_btn3:
    if st.button("📋 Clear Form", use_container_width=True):
        st.session_state.candidate_data = {
            "project_name": "",
            "modality": "IgG_like_bispecific",
            "targets": [],
            "expression_system": "mammalian",
            "sequence_type": "protein",
            "sequence": "",
            "notes": "",
        }
        st.rerun()

# Display current state (debug)
if st.checkbox("📊 Show current data (debug)"):
    st.json({
        "candidate_spec": st.session_state.candidate_data,
        "manufacturing_constraints": st.session_state.constraints_data
    })
