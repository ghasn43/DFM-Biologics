"""
Streamlit Page 3: Manufacturability Report
Display scores, flags, suggestions, and exports
"""

import streamlit as st
import json
import pandas as pd

st.set_page_config(page_title="Manufacturability Report", layout="wide")

st.markdown("# 📊 Manufacturability Report")
st.markdown("Detailed scoring and recommendations")

# Check if scoring has been done
if "score_result" not in st.session_state:
    st.info("👈 Go to **Candidate Input**, click **Score Construct**, then return here")
    st.stop()

result = st.session_state.score_result

# Score summary
st.subheader("Overall Score")

col1, col2, col3, col4, col5 = st.columns(5)

overall = result['overall_score']
color = "🟢" if overall >= 70 else "🟡" if overall >= 50 else "🔴"

with col1:
    st.metric(
        label="Overall Score",
        value=f"{overall}/100",
        delta=f"{overall - 50}",
        delta_color="off"
    )
    st.markdown(f"**{color} Status:** {'Good' if overall >= 70 else 'Fair' if overall >= 50 else 'Review Needed'}")

with col2:
    st.metric(
        label="Sequence Synth",
        value=f"{result['sub_scores']['sequence_synth']}/100"
    )

with col3:
    st.metric(
        label="Assembly Risk",
        value=f"{result['sub_scores']['assembly_risk']}/100"
    )

with col4:
    st.metric(
        label="Developability",
        value=f"{result['sub_scores']['developability']}/100"
    )

with col5:
    st.metric(
        label="Expression Risk",
        value=f"{result['sub_scores']['expression_risk']}/100"
    )

# Interpretation guide
st.markdown("---")
st.subheader("Score Interpretation")
st.markdown("""
- **80–100:** Excellent manufacturability
- **60–79:** Good manufacturability with minor concerns
- **40–59:** Fair manufacturability; design review recommended
- **0–39:** Significant concerns; major design changes needed
""")

# Flags
st.markdown("---")
st.subheader(f"Flags ({len(result['flags'])} total)")

if result['flags']:
    # Filter by severity
    severity_filter = st.selectbox(
        "Filter by severity",
        ["All", "error", "warning", "info"]
    )
    
    filtered_flags = [
        f for f in result['flags']
        if severity_filter == "All" or f['severity'] == severity_filter
    ]
    
    for i, flag in enumerate(filtered_flags, 1):
        severity_icons = {
            "error": "❌",
            "warning": "⚠️",
            "info": "ℹ️"
        }
        icon = severity_icons.get(flag['severity'], "•")
        
        with st.expander(
            f"{icon} [{flag['severity'].upper()}] {flag['category']} — {flag['message'][:60]}..."
        ):
            st.markdown(f"**Category:** {flag['category']}")
            st.markdown(f"**Message:** {flag['message']}")
            if flag['location']:
                st.markdown(f"**Location:** positions {flag['location'][0]}–{flag['location'][1]}")
            st.markdown(f"**Severity:** {flag['severity']}")
else:
    st.success("✅ No flags detected!")

# Suggestions
st.markdown("---")
st.subheader("Design Recommendations")
st.info("💡 **These are high-level suggestions only. No wet-lab instructions are provided.**")

for i, suggestion in enumerate(result['suggestions'], 1):
    st.markdown(f"{i}. {suggestion}")

# Artifacts
st.markdown("---")
st.subheader("Export Report")

col1, col2, col3 = st.columns(3)

with col1:
    # Markdown report
    md_report = result['artifacts']['markdown_report']
    st.download_button(
        label="📄 Download Markdown",
        data=md_report,
        file_name=f"{st.session_state.candidate_data.get('project_name', 'report')}_manufacturability.md",
        mime="text/markdown",
        use_container_width=True
    )

with col2:
    # JSON summary
    json_summary = result['artifacts']['json_summary']
    json_str = json.dumps(json_summary, indent=2)
    st.download_button(
        label="📊 Download JSON",
        data=json_str,
        file_name=f"{st.session_state.candidate_data.get('project_name', 'report')}_summary.json",
        mime="application/json",
        use_container_width=True
    )

with col3:
    # Full result
    full_json = json.dumps(result, indent=2)
    st.download_button(
        label="📋 Full Result",
        data=full_json,
        file_name=f"{st.session_state.candidate_data.get('project_name', 'report')}_full.json",
        mime="application/json",
        use_container_width=True
    )

# Normalized FASTA
st.markdown("---")
st.subheader("Normalized FASTA")

fasta = result['artifacts']['normalized_fasta']
st.code(fasta, language="fasta")

st.download_button(
    label="📥 Download FASTA",
    data=fasta,
    file_name=f"{st.session_state.candidate_data.get('project_name', 'sequence')}.fasta",
    mime="text/plain"
)

# Summary table
st.markdown("---")
st.subheader("Summary")

summary_data = {
    "Project": st.session_state.candidate_data.get('project_name', '—'),
    "Modality": st.session_state.candidate_data.get('modality', '—'),
    "Expression System": st.session_state.candidate_data.get('expression_system', '—'),
    "Targets": ", ".join(st.session_state.candidate_data.get('targets', [])) or '—',
    "Overall Score": result['overall_score'],
    "Flags": len(result['flags']),
    "Errors": len([f for f in result['flags'] if f['severity'] == 'error']),
    "Warnings": len([f for f in result['flags'] if f['severity'] == 'warning']),
}

summary_df = pd.DataFrame([summary_data]).T
summary_df.columns = ["Value"]
st.dataframe(summary_df, use_container_width=True)

# Next steps
st.markdown("---")
st.subheader("Next Steps")

st.markdown(f"""
Based on this analysis (Overall Score: **{overall}/100**):

1. **ℹ️ Review all flags** above, especially errors and warnings
2. **🧪 Consult your molecular biology team** to validate design decisions
3. **🔄 Iterate design** and re-run scoring as needed
4. **📋 Begin experimental planning** once you're satisfied with the design
5. **✅ Perform experimental validation** before manufacturing

**⚠️ Remember:** This tool is for computational planning only. All designs must be:
- Reviewed by experts
- Experimentally validated
- Compliant with biosafety regulations
""")
