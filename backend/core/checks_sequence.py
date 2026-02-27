"""
Sequence-level checks: FASTA parsing, GC analysis, repeats, homopolymers, etc.
"""

from typing import Dict, List, Optional, Tuple

from .utils import (
    calculate_gc_content,
    find_homopolymers,
    find_motif_positions,
    find_palindromes,
    find_repeats,
    is_dna_sequence,
    is_protein_sequence,
    normalize_fasta,
    sliding_window_gc,
)


class SequenceChecker:
    """Validates and analyzes sequence properties."""

    @staticmethod
    def parse_fasta(fasta_input: str) -> tuple[str, Optional[str]]:
        """
        Parse FASTA input.
        Returns (sequence, header_or_none).
        """
        lines = fasta_input.strip().split("\n")
        header = None
        seq = ""
        
        for line in lines:
            line = line.strip()
            if not line:
                continue
            if line.startswith(">"):
                if header is None:
                    header = line[1:]
                else:
                    break
            else:
                seq += line.upper()
        
        return seq, header

    @staticmethod
    def validate_sequence_type(
        sequence: str,
        expected_type: str  # "protein" or "dna_cds"
    ) -> tuple[bool, Optional[str]]:
        """
        Validate that sequence matches expected type.
        Returns (is_valid, error_message_or_none).
        """
        seq = normalize_fasta(sequence)
        
        if expected_type == "protein":
            if is_protein_sequence(seq):
                return True, None
            else:
                return False, "Sequence contains invalid protein characters"
        elif expected_type == "dna_cds":
            if is_dna_sequence(seq):
                return True, None
            else:
                return False, "Sequence contains invalid DNA characters"
        else:
            return False, f"Unknown sequence type: {expected_type}"

    @staticmethod
    def check_gc_windows(
        sequence: str,
        gc_min: float,
        gc_max: float,
        window_size: int = 100
    ) -> List[Dict]:
        """
        Check GC content in sliding windows.
        Returns list of dicts with violations.
        """
        seq = normalize_fasta(sequence)
        if not is_dna_sequence(seq):
            return []
        
        flags = []
        windows = sliding_window_gc(seq, window_size)
        
        for start_pos, gc in windows:
            if gc < gc_min or gc > gc_max:
                severity = "warning"
                if gc < gc_min * 0.5 or gc > gc_max * 1.5:
                    severity = "error"
                
                flags.append({
                    "severity": severity,
                    "category": "gc_content",
                    "message": (
                        f"GC content {gc:.2%} in window [{start_pos}–{start_pos + window_size - 1}] "
                        f"outside range [{gc_min:.0%}–{gc_max:.0%}]"
                    ),
                    "location": [start_pos, start_pos + window_size - 1]
                })
        
        return flags

    @staticmethod
    def check_homopolymers(
        sequence: str,
        max_length: int = 6
    ) -> List[Dict]:
        """
        Check for long homopolymer stretches.
        Returns list of violation flags.
        """
        seq = normalize_fasta(sequence)
        if not is_dna_sequence(seq):
            return []
        
        flags = []
        homopolymers = find_homopolymers(seq, min_length=max_length)
        
        for start, end, base, length in homopolymers:
            severity = "warning"
            if length >= max_length + 3:
                severity = "error"
            
            flags.append({
                "severity": severity,
                "category": "homopolymer",
                "message": (
                    f"Homopolymer {base*length} found at position {start}–{end}, "
                    f"length {length} (threshold {max_length})"
                ),
                "location": [start, end]
            })
        
        return flags

    @staticmethod
    def check_repeats(
        sequence: str,
        kmer_size: int = 6
    ) -> List[Dict]:
        """
        Check for repeated k-mers.
        Returns list of violation flags.
        """
        seq = normalize_fasta(sequence)
        flags = []
        repeats = find_repeats(seq, kmer_size)
        
        if repeats:
            flags.append({
                "severity": "warning",
                "category": "repeat",
                "message": f"Found {len(repeats)} repeated {kmer_size}-mers (may complicate assembly)",
                "location": None
            })
        
        return flags

    @staticmethod
    def check_palindromes(
        sequence: str,
        min_length: int = 8
    ) -> List[Dict]:
        """
        Check for palindromic sequences (hairpin risk).
        Returns list of violation flags.
        """
        seq = normalize_fasta(sequence)
        flags = []
        palindromes = find_palindromes(seq, min_length)
        
        for start, end, subseq in palindromes[:10]:  # Limit to first 10
            flags.append({
                "severity": "info",
                "category": "palindrome",
                "message": (
                    f"Palindromic sequence at {start}–{end}: {subseq} "
                    f"(may form secondary structure)"
                ),
                "location": [start, end]
            })
        
        return flags

    @staticmethod
    def check_forbidden_motifs(
        sequence: str,
        forbidden_motifs: List[str]
    ) -> List[Dict]:
        """
        Check for forbidden sequence motifs.
        Returns list of violation flags.
        """
        seq = normalize_fasta(sequence)
        flags = []
        
        for motif in forbidden_motifs:
            positions = find_motif_positions(seq, motif)
            for start, end in positions:
                flags.append({
                    "severity": "error",
                    "category": "forbidden_motif",
                    "message": f"Forbidden motif '{motif}' found at position {start}–{end}",
                    "location": [start, end]
                })
        
        return flags

    @staticmethod
    def check_restriction_sites(
        sequence: str,
        sites_to_avoid: List[str]
    ) -> List[Dict]:
        """
        Placeholder for restriction site checking.
        (Does not provide lab protocols, only flags locations.)
        """
        # NOTE: This is a placeholder. Real implementation would use a database
        # of restriction enzyme recognition sequences. For safety, we do NOT include
        # that database or detailed protocols here.
        flags = []
        
        # Example mock check (simplified)
        common_sites = {
            "EcoRI": "GAATTC",
            "BamHI": "GGATCC",
            "HindIII": "AAGCTT",
            "XbaI": "TCTAGA",
        }
        
        seq = normalize_fasta(sequence)
        
        for site_name in sites_to_avoid:
            if site_name in common_sites:
                motif = common_sites[site_name]
                positions = find_motif_positions(seq, motif)
                for start, end in positions:
                    flags.append({
                        "severity": "warning",
                        "category": "restriction_site",
                        "message": f"Restriction site {site_name} at position {start}–{end}",
                        "location": [start, end]
                    })
        
        return flags
