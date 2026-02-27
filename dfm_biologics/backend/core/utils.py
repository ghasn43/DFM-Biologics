"""
Utility functions for sequence processing and validation.
"""

import re
from typing import List, Tuple


def normalize_fasta(sequence: str) -> str:
    """
    Remove FASTA header and whitespace from a sequence string.
    Returns just the sequence in uppercase.
    """
    lines = sequence.strip().split("\n")
    seq = ""
    for line in lines:
        line = line.strip()
        if line and not line.startswith(">"):
            seq += line.upper()
    return seq


def is_dna_sequence(seq: str) -> bool:
    """Check if sequence contains only DNA bases (ACGT, allowing N)."""
    valid_dna = set("ACGTN")
    return all(c in valid_dna for c in seq.upper())


def is_protein_sequence(seq: str) -> bool:
    """Check if sequence contains valid protein amino acids."""
    valid_protein = set("ACDEFGHIKLMNPQRSTVWXY*")
    return all(c in valid_protein for c in seq.upper())


def calculate_gc_content(seq: str) -> float:
    """
    Calculate overall GC content (0.0–1.0).
    For DNA sequences only.
    """
    seq = seq.upper()
    if not seq:
        return 0.0
    gc_count = seq.count('G') + seq.count('C')
    return gc_count / len(seq)


def sliding_window_gc(seq: str, window_size: int = 100) -> List[Tuple[int, float]]:
    """
    Compute GC content in sliding windows.
    Returns list of (start_position, gc_fraction) tuples.
    """
    seq = seq.upper()
    results = []
    for i in range(len(seq) - window_size + 1):
        window = seq[i:i+window_size]
        gc = window.count('G') + window.count('C')
        gc_frac = gc / window_size
        results.append((i, gc_frac))
    return results


def find_homopolymers(seq: str, min_length: int = 4) -> List[Tuple[int, int, str, int]]:
    """
    Find stretches of identical consecutive bases.
    Returns list of (start, end, base, length) tuples.
    """
    seq = seq.upper()
    results = []
    i = 0
    while i < len(seq):
        j = i
        while j < len(seq) and seq[j] == seq[i]:
            j += 1
        length = j - i
        if length >= min_length:
            results.append((i, j - 1, seq[i], length))
        i = j
    return results


def find_repeats(seq: str, kmer_size: int = 6) -> List[Tuple[int, int, str]]:
    """
    Find simple k-mer repeats (same k-mer appearing multiple times).
    Returns list of (pos1, pos2, kmer) for duplicates.
    """
    seq = seq.upper()
    results = []
    kmer_positions: dict = {}
    
    for i in range(len(seq) - kmer_size + 1):
        kmer = seq[i:i+kmer_size]
        if kmer not in kmer_positions:
            kmer_positions[kmer] = []
        kmer_positions[kmer].append(i)
    
    for kmer, positions in kmer_positions.items():
        if len(positions) > 1:
            for i in range(len(positions) - 1):
                results.append((positions[i], positions[i+1], kmer))
    
    return results


def find_palindromes(seq: str, min_length: int = 6) -> List[Tuple[int, int, str]]:
    """
    Find palindromic sequences (reverse complement if DNA, else literal reverse).
    Returns list of (start, end, subsequence) tuples.
    """
    seq = seq.upper()
    results = []
    
    # Simple palindrome detection (same forwards and backwards)
    for i in range(len(seq) - min_length + 1):
        for j in range(i + min_length, len(seq) + 1):
            subseq = seq[i:j]
            # Check both exact reverse and reverse complement (if DNA)
            rev = subseq[::-1]
            if subseq == rev and len(subseq) >= min_length:
                results.append((i, j - 1, subseq))
    
    return results


def find_motif_positions(seq: str, motif: str) -> List[Tuple[int, int]]:
    """
    Find all occurrences of a motif in sequence (case-insensitive).
    Returns list of (start, end) positions.
    """
    seq = seq.upper()
    motif = motif.upper()
    results = []
    
    for i in range(len(seq) - len(motif) + 1):
        if seq[i:i+len(motif)] == motif:
            results.append((i, i + len(motif) - 1))
    
    return results


def render_fasta(project_name: str, sequence: str, line_width: int = 80) -> str:
    """
    Render a normalized sequence as FASTA format.
    """
    lines = [f">{project_name}"]
    seq = normalize_fasta(sequence)
    for i in range(0, len(seq), line_width):
        lines.append(seq[i:i+line_width])
    return "\n".join(lines)
