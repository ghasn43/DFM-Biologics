"""
Streamlit Page 2: Construct Architecture
Display construct blueprint and warnings
"""

import streamlit as st
import json

st.set_page_config(page_title="Construct Architecture", layout="wide")

st.markdown("# 🏗️ Construct Architecture")
st.markdown("Abstract blueprint of your construct design")

# Check if blueprint has been generated
if "blueprint_result" not in st.session_state:
    st.info("👈 Go to **Candidate Input** and click **Generate Blueprint** first")
    st.stop()

blueprint = st.session_state.blueprint_result

# Display basic info
col1, col2 = st.columns(2)

with col1:
    st.subheader("Blueprint Summary")
    st.markdown(f"**Chains:** {', '.join(blueprint['chains'])}")
    st.markdown(f"**Domain Count:** {len(blueprint['domains'])}")

with col2:
    st.subheader("Architecture")
    
    # Simple visualization
    modality = st.session_state.candidate_data.get("modality", "Unknown")
    
    if modality == "IgG_like_bispecific":
        st.code("""
HC1 ┓
    ├─ IgG 1
LC1 ┛

HC2 ┓
    ├─ IgG 2 (different specificity)
LC2 ┛
        """)
    elif modality == "VHH_bispecific":
        st.code("""
[VHH1] ―Linker― [VHH2]
Single chain, compact
        """)
    elif modality == "Fab_scFv":
        st.code("""
Fab (Fab_HC, Fab_LC) + scFv
Hybrid format
        """)
    elif modality == "Fc_fusion":
        st.code("""
[Binder] ―Linker― [Fc]
Fusion protein
        """)

# Detailed domain table
st.subheader("Domains")

if blueprint['domains']:
    domain_data = []
    for d in blueprint['domains']:
        domain_data.append({
            "Chain": d['chain'],
            "Domain": d['name'],
            "Start": d.get('start', '—'),
            "End": d.get('end', '—'),
        })
    
    st.dataframe(domain_data, use_container_width=True, hide_index=True)
else:
    st.info("No domains specified (start/end positions can be inferred during development)")

# Warnings
if blueprint['warnings']:
    st.subheader("⚠️ Warnings")
    for i, warning in enumerate(blueprint['warnings'], 1):
        st.warning(f"{i}. {warning}")
else:
    st.success("✅ No warnings detected")

# JSON export
st.subheader("Export Blueprint")

col1, col2 = st.columns(2)

with col1:
    json_str = json.dumps(blueprint, indent=2)
    st.download_button(
        label="📥 Download JSON",
        data=json_str,
        file_name=f"{st.session_state.candidate_data.get('project_name', 'construct')}_blueprint.json",
        mime="application/json"
    )

with col2:
    # Generate markdown description
    md_lines = [
        f"# Construct Blueprint: {st.session_state.candidate_data.get('project_name', 'Unknown')}\n",
        f"**Modality:** {st.session_state.candidate_data.get('modality', 'Unknown')}\n",
        f"**Chains:** {', '.join(blueprint['chains'])}\n\n",
    ]
    
    if blueprint['domains']:
        md_lines.append("## Domains\n")
        for d in blueprint['domains']:
            pos_str = f" ({d['start']}–{d['end']})" if d.get('start') is not None else ""
            md_lines.append(f"- **{d['chain']}**: {d['name']}{pos_str}\n")
    
    if blueprint['warnings']:
        md_lines.append("\n## Warnings\n")
        for w in blueprint['warnings']:
            md_lines.append(f"- {w}\n")
    
    markdown_str = "".join(md_lines)
    
    st.download_button(
        label="📄 Download Markdown",
        data=markdown_str,
        file_name=f"{st.session_state.candidate_data.get('project_name', 'construct')}_blueprint.md",
        mime="text/markdown"
    )

# Next steps
st.markdown("---")
st.info(
    "**Next:** Go to the **Manufacturability Report** page to score this construct and see "
    "detailed recommendations.",
    icon="👉"
)
