"""
Manufacturability scoring engine.
Deterministic scoring logic with full explainability via flags.
"""

import json
from typing import List, Dict, Any

from .checks_sequence import SequenceChecker
from .models import (
    CandidateSpec,
    Flag,
    FlagCategoryEnum,
    FlagSeverityEnum,
    GateResult,
    ManufacturingConstraints,
    SubScores,
    Artifacts,
)
from .utils import (
    calculate_gc_content,
    is_dna_sequence,
    is_protein_sequence,
    normalize_fasta,
    find_motif_positions,
)


class ManufacturabilityScoringEngine:
    """
    Deterministic scoring engine for biotech construct manufacturability.
    """

    def __init__(self):
        self.checker = SequenceChecker()

    def score(
        self,
        candidate_spec: CandidateSpec,
        constraints: ManufacturingConstraints
    ) -> GateResult:
        """
        Score a construct candidate.
        Returns a comprehensive GateResult.
        """
        seq = normalize_fasta(candidate_spec.sequence)
        flags: List[Flag] = []

        # Determine if DNA or protein
        is_dna = is_dna_sequence(seq)
        is_protein = is_protein_sequence(seq)

        # Sequence synthesis score
        synth_score, synth_flags = self._score_sequence_synthesis(
            seq, is_dna, constraints
        )
        flags.extend(synth_flags)

        # Assembly risk score
        assembly_score, assembly_flags = self._score_assembly_risk(
            candidate_spec, seq
        )
        flags.extend(assembly_flags)

        # Developability score (protein-specific)
        dev_score, dev_flags = self._score_developability(seq, is_protein)
        flags.extend(dev_flags)

        # Expression risk score
        expr_score, expr_flags = self._score_expression_risk(
            candidate_spec, seq, is_protein
        )
        flags.extend(expr_flags)

        # Compute overall score as weighted average
        overall_score = int(
            0.35 * synth_score
            + 0.25 * assembly_score
            + 0.25 * dev_score
            + 0.15 * expr_score
        )

        # Generate suggestions
        suggestions = self._generate_suggestions(flags, candidate_spec, constraints)

        # Create artifacts
        artifacts = self._create_artifacts(candidate_spec, flags, candidate_spec)

        return GateResult(
            overall_score=overall_score,
            sub_scores=SubScores(
                sequence_synth=synth_score,
                assembly_risk=assembly_score,
                developability=dev_score,
                expression_risk=expr_score
            ),
            flags=flags,
            suggestions=suggestions,
            artifacts=artifacts
        )

    def _score_sequence_synthesis(
        self,
        seq: str,
        is_dna: bool,
        constraints: ManufacturingConstraints
    ) -> tuple[int, List[Flag]]:
        """
        Score sequence synthesis difficulty.
        Considers GC content, homopolymers, repeats, palindromes, forbidden motifs.
        """
        flags: List[Flag] = []
        penalties = []

        if not is_dna:
            # Protein sequence: convert to rough DNA proxy for some checks
            return 85, flags

        # GC content check
        gc = calculate_gc_content(seq)
        if gc < constraints.gc_min or gc > constraints.gc_max:
            penalty = int(10 * abs(gc - (constraints.gc_min + constraints.gc_max) / 2))
            penalties.append(penalty)
            flags.append(
                Flag(
                    severity=FlagSeverityEnum.warning,
                    category=FlagCategoryEnum.gc_content,
                    message=f"Overall GC content {gc:.1%} outside range [{constraints.gc_min:.0%}–{constraints.gc_max:.0%}]",
                    location=None
                )
            )

        # GC window checks
        from .checks_sequence import SequenceChecker
        window_flags = SequenceChecker.check_gc_windows(seq, constraints.gc_min, constraints.gc_max, 100)
        for wf in window_flags:
            flags.append(Flag(
                severity=FlagSeverityEnum[wf["severity"]],
                category=FlagCategoryEnum.gc_content,
                message=wf["message"],
                location=wf.get("location")
            ))
            penalties.append(5)

        # Homopolymer checks
        homo_flags = SequenceChecker.check_homopolymers(seq, constraints.max_homopolymer)
        for hf in homo_flags:
            flags.append(Flag(
                severity=FlagSeverityEnum[hf["severity"]],
                category=FlagCategoryEnum.homopolymer,
                message=hf["message"],
                location=hf.get("location")
            ))
            penalties.append(8)

        # Repeat checks
        repeat_flags = SequenceChecker.check_repeats(seq, 6)
        for rf in repeat_flags:
            flags.append(Flag(
                severity=FlagSeverityEnum[rf["severity"]],
                category=FlagCategoryEnum.repeat,
                message=rf["message"],
                location=rf.get("location")
            ))
            penalties.append(6)

        # Palindrome checks
        palindrome_flags = SequenceChecker.check_palindromes(seq, 8)
        for pf in palindrome_flags[:5]:  # Limit to top 5
            flags.append(Flag(
                severity=FlagSeverityEnum[pf["severity"]],
                category=FlagCategoryEnum.palindrome,
                message=pf["message"],
                location=pf.get("location")
            ))
            penalties.append(3)

        # Forbidden motif checks
        forbidden_flags = SequenceChecker.check_forbidden_motifs(
            seq, constraints.forbidden_motifs
        )
        for ff in forbidden_flags:
            flags.append(Flag(
                severity=FlagSeverityEnum[ff["severity"]],
                category=FlagCategoryEnum.forbidden_motif,
                message=ff["message"],
                location=ff.get("location")
            ))
            penalties.append(15)

        # Restriction site checks
        restriction_flags = SequenceChecker.check_restriction_sites(
            seq, constraints.restriction_sites_to_avoid
        )
        for rf in restriction_flags:
            flags.append(Flag(
                severity=FlagSeverityEnum[rf["severity"]],
                category=FlagCategoryEnum.restriction_site,
                message=rf["message"],
                location=rf.get("location")
            ))
            penalties.append(5)

        # Compute score: start at 100, subtract penalties (cap at 0)
        total_penalty = sum(penalties)
        score = max(0, 100 - total_penalty)

        return score, flags

    def _score_assembly_risk(
        self,
        candidate_spec: CandidateSpec,
        seq: str
    ) -> tuple[int, List[Flag]]:
        """
        Score assembly complexity based on modality and sequence complexity.
        """
        flags: List[Flag] = []
        penalties = []

        # Modality complexity
        modality_complexity = {
            "IgG_like_bispecific": 20,
            "VHH_bispecific": 5,
            "Fab_scFv": 15,
            "Fc_fusion": 10,
        }
        modality_penalty = modality_complexity.get(candidate_spec.modality, 10)
        penalties.append(modality_penalty)

        # Sequence length
        seq_len = len(seq)
        if seq_len > 400:
            penalties.append(8)
            flags.append(
                Flag(
                    severity=FlagSeverityEnum.info,
                    category=FlagCategoryEnum.assembly_complexity,
                    message=f"Construct length {seq_len} aa/bp is large; synthesis may be more complex",
                    location=None
                )
            )

        # Linker heuristic (simple: look for common linker patterns)
        linker_patterns = ["GGGS", "GGGGGS", "AAAGGG", "EAAK"]
        linker_found = False
        for pattern in linker_patterns:
            if pattern in seq.upper():
                linker_found = True
                break

        if linker_found:
            penalties.append(3)
            flags.append(
                Flag(
                    severity=FlagSeverityEnum.info,
                    category=FlagCategoryEnum.linker_length,
                    message="Linker pattern detected; verify length and flexibility are appropriate",
                    location=None
                )
            )

        total_penalty = sum(penalties)
        score = max(0, 100 - total_penalty)

        return score, flags

    def _score_developability(
        self,
        seq: str,
        is_protein: bool
    ) -> tuple[int, List[Flag]]:
        """
        Score protein developability (glycosylation, deamidation, oxidation, cleavage).
        Only applies to protein sequences.
        """
        flags: List[Flag] = []
        penalties = []

        if not is_protein:
            return 80, flags

        seq = seq.upper()

        # Glycosylation risk (NXST motif, where X != P)
        for i in range(len(seq) - 3):
            if seq[i] == 'N' and seq[i+2] in 'ST' and seq[i+1] != 'P':
                penalties.append(3)
                flags.append(
                    Flag(
                        severity=FlagSeverityEnum.warning,
                        category=FlagCategoryEnum.glycosylation,
                        message=f"Potential N-glycosylation motif '{seq[i:i+4]}' at position {i}–{i+3}",
                        location=[i, i+3]
                    )
                )

        # Deamidation hotspots (NG, NS, NT)
        deamidation_motifs = ["NG", "NS", "NT"]
        for motif in deamidation_motifs:
            positions = find_motif_positions(seq, motif)
            for start, end in positions:
                penalties.append(2)
                flags.append(
                    Flag(
                        severity=FlagSeverityEnum.info,
                        category=FlagCategoryEnum.deamidation,
                        message=f"Deamidation hotspot '{motif}' at position {start}–{end}",
                        location=[start, end]
                    )
                )

        # Oxidation risk (M residues)
        m_count = seq.count('M')
        if m_count > 3:
            penalties.append(2 * (m_count - 3))
            flags.append(
                Flag(
                    severity=FlagSeverityEnum.info,
                    category=FlagCategoryEnum.oxidation,
                    message=f"Multiple methionine residues ({m_count} total); oxidation risk",
                    location=None
                )
            )

        # Proteolytic cleavage risk (basic pair motifs: RR, RK, KR)
        cleavage_motifs = ["RR", "RK", "KR"]
        cleavage_count = 0
        for motif in cleavage_motifs:
            positions = find_motif_positions(seq, motif)
            cleavage_count += len(positions)

        if cleavage_count > 2:
            penalties.append(3)
            flags.append(
                Flag(
                    severity=FlagSeverityEnum.info,
                    category=FlagCategoryEnum.proteolytic_cleavage,
                    message=f"Multiple basic pair motifs ({cleavage_count} total); monitor for proteolytic cleavage",
                    location=None
                )
            )

        total_penalty = sum(penalties)
        score = max(0, 100 - total_penalty)

        return score, flags

    def _score_expression_risk(
        self,
        candidate_spec: CandidateSpec,
        seq: str,
        is_protein: bool
    ) -> tuple[int, List[Flag]]:
        """
        Score expression risk based on system and construct properties.
        """
        flags: List[Flag] = []
        penalties = []

        expr_penalties = {
            "mammalian": 5,
            "yeast": 10,
            "ecoli": 12,
            "cell_free": 8,
        }
        base_penalty = expr_penalties.get(candidate_spec.expression_system, 10)
        penalties.append(base_penalty)

        # Codon bias heuristic (very simple: rare codons)
        if candidate_spec.expression_system == "ecoli" and is_protein:
            # Check for rare codons in E. coli (very simplified)
            rare_codons = {"CUA", "AUA", "GUA"}  # Rare in E. coli
            # This is a placeholder; real implementation would check actual codons
            penalties.append(2)

        # Size-based expression penalty
        seq_len = len(seq)
        if seq_len > 500:
            penalties.append(5)
            flags.append(
                Flag(
                    severity=FlagSeverityEnum.info,
                    category=FlagCategoryEnum.general,
                    message="Large construct may reduce expression levels",
                    location=None
                )
            )

        if seq_len < 50:
            penalties.append(8)
            flags.append(
                Flag(
                    severity=FlagSeverityEnum.warning,
                    category=FlagCategoryEnum.general,
                    message="Very small construct; verify it has sufficient structure",
                    location=None
                )
            )

        total_penalty = sum(penalties)
        score = max(0, 100 - total_penalty)

        return score, flags

    def _generate_suggestions(
        self,
        flags: List[Flag],
        candidate_spec: CandidateSpec,
        constraints: ManufacturingConstraints
    ) -> List[str]:
        """
        Generate high-level design suggestions based on flags.
        Only SAFE suggestions; no lab protocols.
        """
        suggestions = []

        # Count flag categories
        categories = {}
        for flag in flags:
            cat = flag.category
            categories[cat] = categories.get(cat, 0) + 1

        if categories.get("homopolymer", 0) > 0:
            suggestions.append(
                "Reduce long homopolymer stretches (consider alternative codons or sequence variants)"
            )

        if categories.get("gc_content", 0) > 2:
            suggestions.append(
                "Optimize GC content in high-variance windows (target ~50% for synthesis)"
            )

        if categories.get("repeat", 0) > 0:
            suggestions.append(
                "Review and reduce repetitive k-mers to improve assembly fidelity"
            )

        if categories.get("palindrome", 0) > 3:
            suggestions.append(
                "Minimize palindromic sequences to reduce secondary structure formation"
            )

        if candidate_spec.modality == "VHH_bispecific":
            suggestions.append(
                "Verify linker length (typical: 15–30 aa) for optimal inter-domain spacing"
            )

        if candidate_spec.expression_system == "ecoli" and len(flags) > 5:
            suggestions.append(
                "Consider mammalian or cell-free systems for complex constructs"
            )

        if categories.get("glycosylation", 0) > 0:
            suggestions.append(
                "Review N-glycosylation sites; consider mutations if unintended"
            )

        if not suggestions:
            suggestions.append(
                "Construct appears well-optimized; proceed with experimental validation"
            )

        return suggestions

    def _create_artifacts(
        self,
        candidate_spec: CandidateSpec,
        flags: List[Flag],
        spec: CandidateSpec
    ) -> Artifacts:
        """
        Create output artifacts: normalized FASTA, JSON summary, markdown report.
        """
        from .utils import render_fasta

        # Normalized FASTA
        normalized_fasta = render_fasta(candidate_spec.project_name, candidate_spec.sequence)

        # JSON summary
        json_summary = {
            "project": candidate_spec.project_name,
            "modality": candidate_spec.modality,
            "targets": candidate_spec.targets,
            "expression_system": candidate_spec.expression_system,
            "sequence_type": candidate_spec.sequence_type,
            "sequence_length": len(normalize_fasta(candidate_spec.sequence)),
            "flag_count": len(flags),
            "notes": candidate_spec.notes,
        }

        # Markdown report
        markdown_lines = [
            f"# Manufacturability Report: {candidate_spec.project_name}\n",
            f"**Generated:** 2026-02-27\n",
            f"\n## Project Overview\n",
            f"- **Modality:** {candidate_spec.modality}\n",
            f"- **Expression System:** {candidate_spec.expression_system}\n",
            f"- **Targets:** {', '.join(candidate_spec.targets) or '(none specified)'}\n",
            f"- **Sequence Type:** {candidate_spec.sequence_type}\n",
            f"- **Length:** {len(normalize_fasta(candidate_spec.sequence))} bp/aa\n",
        ]

        if candidate_spec.notes:
            markdown_lines.append(f"\n**Notes:** {candidate_spec.notes}\n")

        markdown_lines.append(f"\n## Flags\n")
        if flags:
            for i, flag in enumerate(flags, 1):
                markdown_lines.append(
                    f"{i}. **[{flag.severity.upper()}]** {flag.message}\n"
                )
        else:
            markdown_lines.append("No issues flagged.\n")

        markdown_report = "".join(markdown_lines)

        return Artifacts(
            normalized_fasta=normalized_fasta,
            json_summary=json_summary,
            markdown_report=markdown_report
        )
