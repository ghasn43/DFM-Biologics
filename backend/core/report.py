"""
Report generation and formatting.
"""

from typing import Any, Dict, List

from .models import GateResult, CandidateSpec


class ReportGenerator:
    """Generate formatted reports from GateResult."""

    @staticmethod
    def generate_markdown(
        gate_result: GateResult,
        candidate_spec: CandidateSpec
    ) -> str:
        """
        Generate a comprehensive markdown report.
        """
        lines = [
            f"# Manufacturability Gate Report\n",
            f"\n**Project:** {candidate_spec.project_name}\n",
            f"**Generated:** 2026-02-27\n",
            f"\n---\n",
            f"\n## ⚠️ Safety Notice\n",
            f"This report is for **computational planning and risk assessment only**.\n",
            f"It does NOT provide wet-lab instructions and must NOT be used for harmful bioengineering.\n",
            f"All designs require experimental validation and compliance with regulatory requirements.\n",
            f"\n---\n",
            f"\n## Scoring Summary\n",
            f"\n| Metric | Score |\n",
            f"|--------|-------|\n",
            f"| **Overall Score** | **{gate_result.overall_score}/100** |\n",
            f"| Sequence Synthesis | {gate_result.sub_scores.sequence_synth}/100 |\n",
            f"| Assembly Risk | {gate_result.sub_scores.assembly_risk}/100 |\n",
            f"| Developability | {gate_result.sub_scores.developability}/100 |\n",
            f"| Expression Risk | {gate_result.sub_scores.expression_risk}/100 |\n",
            f"\n",
        ]

        # Design details
        lines.extend([
            f"\n## Design Details\n",
            f"- **Modality:** {candidate_spec.modality}\n",
            f"- **Expression System:** {candidate_spec.expression_system}\n",
            f"- **Targets:** {', '.join(candidate_spec.targets) if candidate_spec.targets else '(None)'}\n",
            f"- **Sequence Type:** {candidate_spec.sequence_type}\n",
        ])

        if candidate_spec.notes:
            lines.append(f"- **Notes:** {candidate_spec.notes}\n")

        # Flags
        lines.append(f"\n## Issues & Recommendations\n")
        if gate_result.flags:
            for i, flag in enumerate(gate_result.flags, 1):
                severity_icon = {
                    "info": "ℹ️",
                    "warning": "⚠️",
                    "error": "❌",
                }.get(flag.severity, "•")
                
                lines.append(
                    f"\n### {i}. {severity_icon} [{flag.severity.upper()}] {flag.category}\n"
                )
                lines.append(f"{flag.message}\n")
                if flag.location:
                    lines.append(f"*Location: positions {flag.location[0]}–{flag.location[1]}*\n")
        else:
            lines.append("✅ No critical issues detected.\n")

        # Suggestions
        lines.append(f"\n## Recommendations\n")
        for i, suggestion in enumerate(gate_result.suggestions, 1):
            lines.append(f"{i}. {suggestion}\n")

        # Artifacts info
        lines.extend([
            f"\n---\n",
            f"\n## Next Steps\n",
            f"1. Review this report and all flagged issues\n",
            f"2. Consult with your molecular biology team\n",
            f"3. Implement recommended design changes\n",
            f"4. Perform experimental validation\n",
            f"5. Comply with all regulatory and biosafety requirements\n",
        ])

        return "".join(lines)

    @staticmethod
    def generate_json(gate_result: GateResult, candidate_spec: CandidateSpec) -> Dict[str, Any]:
        """
        Generate a JSON-serializable summary.
        """
        return {
            "project": candidate_spec.project_name,
            "overall_score": gate_result.overall_score,
            "sub_scores": {
                "sequence_synth": gate_result.sub_scores.sequence_synth,
                "assembly_risk": gate_result.sub_scores.assembly_risk,
                "developability": gate_result.sub_scores.developability,
                "expression_risk": gate_result.sub_scores.expression_risk,
            },
            "flags": [
                {
                    "severity": flag.severity,
                    "category": flag.category,
                    "message": flag.message,
                    "location": flag.location,
                }
                for flag in gate_result.flags
            ],
            "suggestions": gate_result.suggestions,
            "summary": {
                "modality": candidate_spec.modality,
                "expression_system": candidate_spec.expression_system,
                "targets": candidate_spec.targets,
                "sequence_type": candidate_spec.sequence_type,
            },
        }
