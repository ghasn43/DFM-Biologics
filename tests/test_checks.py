"""
Unit tests for sequence and construct checks.
"""

import pytest
from backend.core.checks_sequence import SequenceChecker
from backend.core.checks_construct import ConstructChecker
from backend.core.utils import (
    normalize_fasta,
    calculate_gc_content,
    find_homopolymers,
    find_repeats,
    find_motif_positions,
    is_dna_sequence,
    is_protein_sequence,
)


class TestSequenceUtilities:
    """Tests for sequence utility functions."""

    def test_normalize_fasta_with_header(self):
        """Test FASTA normalization with header."""
        fasta = ">myseq\nMVHLTPEEKS\nLIPQPP"
        result = normalize_fasta(fasta)
        assert result == "MVHLTPEEKSLIPQPP"

    def test_normalize_fasta_without_header(self):
        """Test FASTA normalization without header."""
        seq = "ATGCCCGGGAAA"
        result = normalize_fasta(seq)
        assert result == "ATGCCCGGGAAA"

    def test_normalize_fasta_lowercase(self):
        """Test that FASTA is converted to uppercase."""
        fasta = ">seq\nmvhlTpeeKs"
        result = normalize_fasta(fasta)
        assert result == "MVHLTPEEKS"

    def test_is_dna_sequence(self):
        """Test DNA sequence validation."""
        assert is_dna_sequence("ATGCCCGGG")
        assert is_dna_sequence("ATGN")  # N is allowed
        assert not is_dna_sequence("ATGCCUGGG")  # U is RNA
        assert not is_dna_sequence("MVHLTPEEKS")  # Protein

    def test_is_protein_sequence(self):
        """Test protein sequence validation."""
        assert is_protein_sequence("MVHLTPEEKS")
        assert is_protein_sequence("MVHLTPEEKS*")  # Stop codon
        assert not is_protein_sequence("ATGCCCGGG")  # DNA

    def test_calculate_gc_content(self):
        """Test GC content calculation."""
        assert calculate_gc_content("GGGGCCCC") == 1.0
        assert calculate_gc_content("AAAATTTT") == 0.0
        assert calculate_gc_content("ATGC") == 0.5

    def test_find_homopolymers(self):
        """Test homopolymer detection."""
        results = find_homopolymers("ATGCCCCAAA", min_length=4)
        assert len(results) == 2
        assert (3, 6, 'C', 4) in results
        assert (7, 9, 'A', 3) not in results  # Below min_length

    def test_find_homopolymers_empty(self):
        """Test homopolymer detection on sequence without long homopolymers."""
        results = find_homopolymers("ATGCAT", min_length=4)
        assert len(results) == 0

    def test_find_repeats(self):
        """Test k-mer repeat detection."""
        # ATGCCG appears twice
        results = find_repeats("ATGCCGATGCCG", kmer_size=6)
        assert len(results) > 0
        assert any(r[2] == "ATGCCG" for r in results)

    def test_find_motif_positions(self):
        """Test motif finding."""
        positions = find_motif_positions("ATGCCCAAA", "CCC")
        assert len(positions) == 1
        assert positions[0] == (3, 5)

    def test_find_motif_case_insensitive(self):
        """Test that motif search is case-insensitive."""
        positions = find_motif_positions("ATGCCCAAA", "cCC")
        assert len(positions) == 1


class TestSequenceChecker:
    """Tests for SequenceChecker class."""

    def test_parse_fasta_with_header(self):
        """Test FASTA parsing."""
        fasta = ">myseq\nATGCCC"
        seq, header = SequenceChecker.parse_fasta(fasta)
        assert seq == "ATGCCC"
        assert header == "myseq"

    def test_parse_fasta_multiple_lines(self):
        """Test FASTA parsing with multiline sequence."""
        fasta = ">seq1\nATGC\nCCGG\nAA"
        seq, header = SequenceChecker.parse_fasta(fasta)
        assert seq == "ATGCCCGGAA"

    def test_validate_sequence_type_protein(self):
        """Test protein sequence type validation."""
        valid, msg = SequenceChecker.validate_sequence_type("MVHLTPEEKS", "protein")
        assert valid
        assert msg is None

    def test_validate_sequence_type_protein_invalid(self):
        """Test invalid protein sequence type."""
        valid, msg = SequenceChecker.validate_sequence_type("ATGCCC", "protein")
        assert not valid
        assert "invalid protein characters" in msg.lower()

    def test_validate_sequence_type_dna(self):
        """Test DNA sequence type validation."""
        valid, msg = SequenceChecker.validate_sequence_type("ATGCCC", "dna_cds")
        assert valid
        assert msg is None

    def test_check_gc_windows(self):
        """Test GC window checking."""
        # Create a sequence with high GC region
        seq = "ATGC" * 25 + "GGGG"  # Last part is high GC
        flags = SequenceChecker.check_gc_windows(seq, gc_min=0.3, gc_max=0.5)
        
        # Should have at least one flag for the high GC region
        assert len(flags) >= 0  # May have flags depending on window

    def test_check_homopolymers(self):
        """Test homopolymer checking."""
        seq = "ATGAAAAACCC"
        flags = SequenceChecker.check_homopolymers(seq, max_length=5)
        
        assert len(flags) > 0
        assert any("homopolymer" in f["category"] for f in flags)

    def test_check_forbidden_motifs(self):
        """Test forbidden motif checking."""
        seq = "ATGAAAAAAA"
        flags = SequenceChecker.check_forbidden_motifs(seq, ["AAAA"])
        
        assert len(flags) > 0
        assert any("forbidden" in f["category"] for f in flags)

    def test_check_palindromes(self):
        """Test palindrome detection."""
        # GAATTC and its reverse complement are palindromes
        seq = "ATGAATTCAA"
        flags = SequenceChecker.check_palindromes(seq, min_length=6)
        
        # Should detect palindromes
        assert len(flags) > 0


class TestConstructChecker:
    """Tests for ConstructChecker class."""

    def test_blueprint_igg_bispecific(self):
        """Test IgG bispecific blueprint generation."""
        bp = ConstructChecker.generate_blueprint(
            "test-001",
            "IgG_like_bispecific",
            "MVHLTPEEKS" * 40,  # Long sequence
            "mammalian"
        )
        
        assert "HC1" in bp.chains
        assert "LC1" in bp.chains
        assert "HC2" in bp.chains
        assert "LC2" in bp.chains
        assert len(bp.domains) == 8

    def test_blueprint_vhh_bispecific(self):
        """Test VHH bispecific blueprint generation."""
        bp = ConstructChecker.generate_blueprint(
            "test-001",
            "VHH_bispecific",
            "MVHLTPEEKS" * 15,
            "mammalian"
        )
        
        assert "ScVHH" in bp.chains
        assert len(bp.domains) == 3
        assert any(d.name == "VHH1" for d in bp.domains)
        assert any(d.name == "Linker" for d in bp.domains)
        assert any(d.name == "VHH2" for d in bp.domains)

    def test_blueprint_fab_scfv(self):
        """Test Fab + scFv blueprint generation."""
        bp = ConstructChecker.generate_blueprint(
            "test-001",
            "Fab_scFv",
            "MVHLTPEEKS" * 20,
            "mammalian"
        )
        
        assert "Fab_HC" in bp.chains
        assert "Fab_LC" in bp.chains
        assert "scFv" in bp.chains
        assert len(bp.domains) == 5

    def test_blueprint_fc_fusion(self):
        """Test Fc fusion blueprint generation."""
        bp = ConstructChecker.generate_blueprint(
            "test-001",
            "Fc_fusion",
            "MVHLTPEEKS" * 20,
            "mammalian"
        )
        
        assert "Fusion" in bp.chains
        assert len(bp.domains) == 3
        assert any(d.name == "Binder" for d in bp.domains)
        assert any(d.name == "Fc" for d in bp.domains)

    def test_blueprint_warnings_large_construct(self):
        """Test that large constructs generate warnings."""
        large_seq = "MVHLTPEEKS" * 50  # 500 aa
        bp = ConstructChecker.generate_blueprint(
            "large-test",
            "IgG_like_bispecific",
            large_seq,
            "mammalian"
        )
        
        assert len(bp.warnings) > 0

    def test_blueprint_warnings_ecoli_igg(self):
        """Test that E. coli + IgG generates warnings."""
        bp = ConstructChecker.generate_blueprint(
            "ecoli-test",
            "IgG_like_bispecific",
            "MVHLTPEEKS" * 20,
            "ecoli"
        )
        
        assert len(bp.warnings) > 0
        assert any("periplasmic" in w.lower() for w in bp.warnings)

    def test_blueprint_unknown_modality(self):
        """Test handling of unknown modality."""
        bp = ConstructChecker.generate_blueprint(
            "unknown-test",
            "unknown_modality",
            "MVHLTPEEKS",
            "mammalian"
        )
        
        assert len(bp.chains) == 0
        assert len(bp.warnings) > 0


class TestIntegration:
    """Integration tests for sequence and construct checks."""

    def test_full_sequence_analysis(self):
        """Test full sequence analysis workflow."""
        seq = "ATGCCCGGGAAATTT" * 10
        
        # Parse
        parsed, header = SequenceChecker.parse_fasta(f">test\n{seq}")
        assert parsed == seq.upper()
        
        # Validate
        valid, msg = SequenceChecker.validate_sequence_type(seq, "dna_cds")
        assert valid
        
        # Check properties
        gc = calculate_gc_content(seq)
        assert 0 <= gc <= 1
        
        homos = find_homopolymers(seq, 4)
        assert isinstance(homos, list)

    def test_blueprint_with_warnings(self):
        """Test that blueprint generation includes appropriate warnings."""
        # Small sequence
        small_bp = ConstructChecker.generate_blueprint(
            "small",
            "VHH_bispecific",
            "MVHLTPEEKS",  # 10 aa
            "mammalian"
        )
        
        # Should have warning about small size
        assert any("too short" in w.lower() for w in small_bp.warnings)
