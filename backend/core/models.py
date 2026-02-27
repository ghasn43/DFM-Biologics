"""
Pydantic models for construct design and manufacturability assessment.
All models include validation and are designed for safety and clarity.
"""

from enum import Enum
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field, field_validator


class ModalityEnum(str, Enum):
    """Supported protein construct modalities."""
    IgG_like_bispecific = "IgG_like_bispecific"
    VHH_bispecific = "VHH_bispecific"
    Fab_scFv = "Fab_scFv"
    Fc_fusion = "Fc_fusion"


class ExpressionSystemEnum(str, Enum):
    """Supported expression systems."""
    mammalian = "mammalian"
    yeast = "yeast"
    ecoli = "ecoli"
    cell_free = "cell_free"


class SequenceTypeEnum(str, Enum):
    """Type of input sequence."""
    protein = "protein"
    dna_cds = "dna_cds"


class CandidateSpec(BaseModel):
    """
    Input specification for a protein construct candidate.
    """
    project_name: str = Field(..., min_length=1, max_length=256, description="Project identifier")
    modality: ModalityEnum = Field(..., description="Construct architecture type")
    targets: List[str] = Field(
        default_factory=list,
        description="Target antigens (e.g., HER2, HER3, any string allowed)"
    )
    expression_system: ExpressionSystemEnum = Field(..., description="Production system")
    sequence_type: SequenceTypeEnum = Field(..., description="DNA CDS or protein sequence")
    sequence: str = Field(..., min_length=3, description="DNA or protein sequence (FASTA accepted)")
    notes: Optional[str] = Field(None, max_length=512, description="Design notes")

    @field_validator('sequence')
    def sequence_not_empty(cls, v: str) -> str:
        """Ensure sequence is non-empty after stripping."""
        clean = v.strip().upper()
        if not clean:
            raise ValueError("Sequence cannot be empty")
        return clean


class ManufacturingConstraints(BaseModel):
    """
    Manufacturing constraints for scoring.
    """
    max_fragment_length: int = Field(
        default=500,
        ge=50,
        le=5000,
        description="Maximum fragment length (bp or aa)"
    )
    gc_min: float = Field(
        default=0.3,
        ge=0.0,
        le=1.0,
        description="Minimum GC content (0.0–1.0)"
    )
    gc_max: float = Field(
        default=0.7,
        ge=0.0,
        le=1.0,
        description="Maximum GC content (0.0–1.0)"
    )
    max_homopolymer: int = Field(
        default=6,
        ge=3,
        le=15,
        description="Maximum consecutive identical base pairs"
    )
    forbidden_motifs: List[str] = Field(
        default_factory=list,
        description="Forbidden sequence motifs (case-insensitive)"
    )
    restriction_sites_to_avoid: List[str] = Field(
        default_factory=list,
        description="Restriction enzyme names to avoid (e.g., EcoRI, BamHI)"
    )
    vendor_profile: str = Field(
        default="generic",
        description="Vendor constraint profile (generic, twist_like, idt_like)"
    )

    @field_validator('gc_min', 'gc_max')
    def validate_gc_range(cls, v: float) -> float:
        """Validate GC content range."""
        if not (0.0 <= v <= 1.0):
            raise ValueError("GC content must be between 0.0 and 1.0")
        return v


class FlagSeverityEnum(str, Enum):
    """Severity levels for flags."""
    info = "info"
    warning = "warning"
    error = "error"


class FlagCategoryEnum(str, Enum):
    """Flag categories."""
    gc_content = "gc_content"
    homopolymer = "homopolymer"
    repeat = "repeat"
    palindrome = "palindrome"
    forbidden_motif = "forbidden_motif"
    restriction_site = "restriction_site"
    glycosylation = "glycosylation"
    deamidation = "deamidation"
    oxidation = "oxidation"
    proteolytic_cleavage = "proteolytic_cleavage"
    codon_bias = "codon_bias"
    assembly_complexity = "assembly_complexity"
    linker_length = "linker_length"
    general = "general"


class Flag(BaseModel):
    """
    A single flag/issue found during scoring.
    """
    severity: FlagSeverityEnum = Field(..., description="Severity level")
    category: FlagCategoryEnum = Field(..., description="Issue category")
    message: str = Field(..., description="Human-readable message")
    location: Optional[List[int]] = Field(
        None,
        description="[start, end] position(s) in sequence (0-indexed, inclusive)"
    )


class SubScores(BaseModel):
    """Sub-component scores."""
    sequence_synth: int = Field(..., ge=0, le=100, description="Sequence synthesis difficulty (0–100)")
    assembly_risk: int = Field(..., ge=0, le=100, description="Assembly complexity (0–100)")
    developability: int = Field(..., ge=0, le=100, description="Developability risk (0–100)")
    expression_risk: int = Field(..., ge=0, le=100, description="Expression risk (0–100)")


class Artifacts(BaseModel):
    """Output artifacts."""
    normalized_fasta: str = Field(..., description="Normalized FASTA sequence")
    json_summary: Dict[str, Any] = Field(default_factory=dict, description="JSON summary")
    markdown_report: str = Field(..., description="Markdown-formatted report")


class GateResult(BaseModel):
    """
    Manufacturability gate scoring result.
    """
    overall_score: int = Field(..., ge=0, le=100, description="Overall manufacturability score (0–100)")
    sub_scores: SubScores = Field(..., description="Component scores")
    flags: List[Flag] = Field(default_factory=list, description="Issues and risks found")
    suggestions: List[str] = Field(default_factory=list, description="High-level design suggestions")
    artifacts: Artifacts = Field(..., description="Output artifacts (FASTA, JSON, markdown)")


class Domain(BaseModel):
    """
    A functional domain within a construct blueprint.
    """
    chain: str = Field(..., description="Chain identifier (e.g., HC1, LC1)")
    name: str = Field(..., description="Domain name (e.g., VH, CH1)")
    start: Optional[int] = Field(None, description="Start position (0-indexed, optional)")
    end: Optional[int] = Field(None, description="End position (0-indexed, inclusive, optional)")


class ConstructBlueprint(BaseModel):
    """
    Abstract blueprint of a construct architecture.
    """
    chains: List[str] = Field(..., description="List of chain identifiers")
    domains: List[Domain] = Field(default_factory=list, description="Domains within the construct")
    warnings: List[str] = Field(default_factory=list, description="Warnings about the design")


class ScoringRequest(BaseModel):
    """
    API request for scoring.
    """
    candidate_spec: CandidateSpec
    manufacturing_constraints: ManufacturingConstraints


class HealthResponse(BaseModel):
    """Health check response."""
    status: str = Field(..., description="Status (e.g., 'ok')")
    version: str = Field(..., description="API version")
