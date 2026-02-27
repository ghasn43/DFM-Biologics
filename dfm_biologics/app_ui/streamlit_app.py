"""
DFM Biologics Streamlit Frontend
Main entry point for the UI
"""

import streamlit as st

st.set_page_config(
    page_title="DFM Biologics",
    page_icon="🧬",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom styling
st.markdown("""
<style>
    .sidebar-warning {
        background-color: #fff3cd;
        border-left: 4px solid #ffc107;
        padding: 1rem;
        margin-bottom: 1rem;
        border-radius: 0.25rem;
    }
    .main-header {
        color: #0d5f91;
        font-weight: bold;
    }
</style>
""", unsafe_allow_html=True)

# Sidebar safety notice
with st.sidebar:
    st.markdown("""
    ### ⚠️ SAFETY NOTICE

    **This tool is for computational planning only.**

    ✅ What this tool does:
    - Analyzes sequence properties
    - Scores manufacturability risks
    - Generates construct blueprints
    - Suggests design improvements

    ❌ What this tool DOES NOT do:
    - Provide wet-lab protocols
    - Replace expert review
    - Enable harmful bioengineering

    **All designs must be:**
    1. Reviewed by molecular biologists
    2. Experimentally validated
    3. Compliant with biosafety regulations
    """)

    st.markdown("---")
    st.markdown("""
    ### 📚 Navigation

    Use the pages on the left to:
    1. **Input** sequences and parameters
    2. **View** construct architecture
    3. **Analyze** manufacturability scores
    """)

# Main page
st.markdown("# 🧬 DFM Biologics")
st.markdown("**Construct Builder & Manufacturability Gate**")

st.markdown("""
A SAFE, in-silico tool for biotech construct design and risk assessment.

## Quick Start

1. **Go to Candidate Input** (page 1) to paste your sequence and set parameters
2. **View Construct Architecture** (page 2) to see the construct blueprint
3. **Check Manufacturability Report** (page 3) for scores and recommendations

## Features

- ✅ **Sequence Analysis:** GC content, repeats, homopolymers, forbidden motifs
- ✅ **Construct Blueprints:** Abstract architecture for multiple modalities
- ✅ **Manufacturability Scoring:** Composite score across synthesis, assembly, developability, expression
- ✅ **Detailed Reporting:** Flags with locations, suggestions, exportable formats

## Supported Modalities

- IgG-like bispecific (2×2 array)
- VHH bispecific (single-chain)
- Fab + scFv (hybrid)
- Fc fusion (fusion protein)

## Supported Expression Systems

- Mammalian (CHO, HEK293)
- Yeast (P. pastoris, S. cerevisiae)
- E. coli
- Cell-free in vitro

---

### ⚠️ Important Disclaimer

**This tool is experimental and for research use only.** Before using any output:

1. Obtain expert molecular biologist review
2. Verify compliance with institutional biosafety requirements
3. Follow all regulatory guidelines (including DURC policies)
4. Perform experimental validation

**Do not use this tool for harmful bioengineering.** All users must adhere to responsible innovation principles.
""")

st.info(
    "👉 **Next Step:** Go to the **Candidate Input** page to get started!",
    icon="👉"
)
