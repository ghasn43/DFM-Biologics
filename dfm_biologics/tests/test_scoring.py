"""
Unit tests for scoring module and scoring logic.
"""

import pytest
from backend.core.models import (
    CandidateSpec,
    ManufacturingConstraints,
    ExpressionSystemEnum,
    SequenceTypeEnum,
    ModalityEnum,
)
from backend.core.scoring import ManufacturabilityScoringEngine


class TestManufacturabilityScoringEngine:
    """Tests for the scoring engine."""

    @pytest.fixture
    def engine(self):
        """Initialize scoring engine."""
        return ManufacturabilityScoringEngine()

    @pytest.fixture
    def simple_protein_spec(self):
        """Simple protein candidate spec."""
        return CandidateSpec(
            project_name="test-001",
            modality=ModalityEnum.VHH_bispecific,
            targets=["HER2"],
            expression_system=ExpressionSystemEnum.mammalian,
            sequence_type=SequenceTypeEnum.protein,
            sequence="MVHLTPEEKSLIP",
            notes="Test candidate"
        )

    @pytest.fixture
    def simple_dna_spec(self):
        """Simple DNA candidate spec."""
        return CandidateSpec(
            project_name="test-dna-001",
            modality=ModalityEnum.VHH_bispecific,
            targets=["HER2"],
            expression_system=ExpressionSystemEnum.mammalian,
            sequence_type=SequenceTypeEnum.dna_cds,
            sequence="ATGGTGCACCTGACACCGGAG",
            notes="Test DNA"
        )

    @pytest.fixture
    def default_constraints(self):
        """Default manufacturing constraints."""
        return ManufacturingConstraints(
            max_fragment_length=500,
            gc_min=0.3,
            gc_max=0.7,
            max_homopolymer=6,
            forbidden_motifs=[],
            restriction_sites_to_avoid=[],
            vendor_profile="generic"
        )

    def test_score_determinism(self, engine, simple_protein_spec, default_constraints):
        """
        Test that scoring is deterministic: same input produces same output.
        """
        result1 = engine.score(simple_protein_spec, default_constraints)
        result2 = engine.score(simple_protein_spec, default_constraints)
        
        assert result1.overall_score == result2.overall_score
        assert result1.sub_scores.sequence_synth == result2.sub_scores.sequence_synth
        assert result1.sub_scores.assembly_risk == result2.sub_scores.assembly_risk
        assert result1.sub_scores.developability == result2.sub_scores.developability
        assert result1.sub_scores.expression_risk == result2.sub_scores.expression_risk
        assert len(result1.flags) == len(result2.flags)

    def test_score_range(self, engine, simple_protein_spec, default_constraints):
        """Test that all scores are within 0-100."""
        result = engine.score(simple_protein_spec, default_constraints)
        
        assert 0 <= result.overall_score <= 100
        assert 0 <= result.sub_scores.sequence_synth <= 100
        assert 0 <= result.sub_scores.assembly_risk <= 100
        assert 0 <= result.sub_scores.developability <= 100
        assert 0 <= result.sub_scores.expression_risk <= 100

    def test_score_has_artifacts(self, engine, simple_protein_spec, default_constraints):
        """Test that scoring produces artifacts."""
        result = engine.score(simple_protein_spec, default_constraints)
        
        assert result.artifacts.normalized_fasta
        assert "MVHLTPEEKSLIP" in result.artifacts.normalized_fasta
        assert result.artifacts.json_summary
        assert result.artifacts.markdown_report

    def test_dna_sequence_scoring(self, engine, simple_dna_spec, default_constraints):
        """Test scoring of DNA sequences."""
        result = engine.score(simple_dna_spec, default_constraints)
        
        assert result.overall_score is not None
        assert 0 <= result.overall_score <= 100

    def test_forbidden_motifs_flag(self, engine, simple_dna_spec, default_constraints):
        """Test that forbidden motifs generate flags."""
        # Add a forbidden motif that exists in the sequence
        default_constraints.forbidden_motifs = ["GTG"]  # Present in ATGGTGCACCTG
        result = engine.score(simple_dna_spec, default_constraints)
        
        forbidden_flags = [f for f in result.flags if f.category == "forbidden_motif"]
        assert len(forbidden_flags) > 0

    def test_gc_content_penalty(self, engine, default_constraints):
        """Test that high GC content generates penalties."""
        high_gc_spec = CandidateSpec(
            project_name="high-gc",
            modality=ModalityEnum.VHH_bispecific,
            targets=["HER2"],
            expression_system=ExpressionSystemEnum.mammalian,
            sequence_type=SequenceTypeEnum.dna_cds,
            sequence="GGGGCCCCGGGGCCCCGGGG",  # High GC
            notes="High GC test"
        )
        
        # Strict constraints
        constraints = ManufacturingConstraints(
            gc_min=0.3,
            gc_max=0.5
        )
        
        result = engine.score(high_gc_spec, constraints)
        gc_flags = [f for f in result.flags if f.category == "gc_content"]
        
        assert len(gc_flags) > 0
        assert result.sub_scores.sequence_synth < 85

    def test_homopolymer_detection(self, engine, default_constraints):
        """Test that long homopolymers are detected."""
        homo_spec = CandidateSpec(
            project_name="homopolymer-test",
            modality=ModalityEnum.VHH_bispecific,
            targets=["HER2"],
            expression_system=ExpressionSystemEnum.mammalian,
            sequence_type=SequenceTypeEnum.dna_cds,
            sequence="ATGAAAAAAAACCC",  # 8 As in a row
            notes="Homopolymer test"
        )
        
        result = engine.score(homo_spec, default_constraints)
        homo_flags = [f for f in result.flags if f.category == "homopolymer"]
        
        assert len(homo_flags) > 0

    def test_expression_system_penalty(self, engine, simple_protein_spec, default_constraints):
        """Test that different expression systems affect scoring."""
        results = {}
        
        for system in [ExpressionSystemEnum.mammalian, ExpressionSystemEnum.ecoli]:
            spec = CandidateSpec(
                project_name=f"test-{system}",
                modality=ModalityEnum.VHH_bispecific,
                targets=["HER2"],
                expression_system=system,
                sequence_type=SequenceTypeEnum.protein,
                sequence="MVHLTPEEKSLIP",
                notes="System test"
            )
            result = engine.score(spec, default_constraints)
            results[str(system)] = result.sub_scores.expression_risk
        
        # E. coli should have different scoring than mammalian
        assert results["ExpressionSystemEnum.ecoli"] != results["ExpressionSystemEnum.mammalian"]

    def test_modality_complexity(self, engine, default_constraints):
        """Test that different modalities affect assembly risk scores."""
        results = {}
        
        for modality in [
            ModalityEnum.IgG_like_bispecific,
            ModalityEnum.VHH_bispecific,
        ]:
            spec = CandidateSpec(
                project_name=f"test-{modality}",
                modality=modality,
                targets=["HER2"],
                expression_system=ExpressionSystemEnum.mammalian,
                sequence_type=SequenceTypeEnum.protein,
                sequence="MVHLTPEEKSLIP",
                notes="Modality test"
            )
            result = engine.score(spec, default_constraints)
            results[str(modality)] = result.sub_scores.assembly_risk
        
        # Assembly scores should differ (IgG is more complex)
        assert results["ModalityEnum.IgG_like_bispecific"] <= results["ModalityEnum.VHH_bispecific"]

    def test_suggestions_on_flags(self, engine, default_constraints):
        """Test that suggestions are generated based on flags."""
        homo_spec = CandidateSpec(
            project_name="suggestion-test",
            modality=ModalityEnum.VHH_bispecific,
            targets=["HER2"],
            expression_system=ExpressionSystemEnum.mammalian,
            sequence_type=SequenceTypeEnum.dna_cds,
            sequence="ATGAAAAAAAACCCGGGGGG",  # Homopolymer + high GC
            notes="Suggestion test"
        )
        
        result = engine.score(homo_spec, default_constraints)
        
        assert len(result.suggestions) > 0
        assert any("homopolymer" in s.lower() for s in result.suggestions)


class TestScoringIntegration:
    """Integration tests for scoring with various inputs."""

    def test_fasta_format_handling(self):
        """Test that FASTA format sequences are handled correctly."""
        from backend.core.utils import normalize_fasta
        
        fasta_seq = """>HER2Bispecific_v1
MVHLTPEEKS
LIPQPPGGGG"""
        
        normalized = normalize_fasta(fasta_seq)
        assert normalized == "MVHLTPEEKSLIPQPPGGGG"

    def test_full_scoring_workflow(self):
        """Test a complete scoring workflow."""
        engine = ManufacturabilityScoringEngine()
        
        spec = CandidateSpec(
            project_name="integration-test",
            modality=ModalityEnum.VHH_bispecific,
            targets=["HER2", "HER3"],
            expression_system=ExpressionSystemEnum.mammalian,
            sequence_type=SequenceTypeEnum.protein,
            sequence="MVHLTPEEKSLIPQPPGGGGAAAA",
            notes="Integration test"
        )
        
        constraints = ManufacturingConstraints(
            max_fragment_length=500,
            gc_min=0.3,
            gc_max=0.7,
            max_homopolymer=5,
            forbidden_motifs=["AAAA"],
        )
        
        result = engine.score(spec, constraints)
        
        # Verify all fields are populated
        assert result.overall_score is not None
        assert result.sub_scores is not None
        assert result.flags is not None
        assert result.suggestions is not None
        assert result.artifacts is not None
        
        # Should have flags for forbidden motif and long homopolymers
        assert len(result.flags) > 0
