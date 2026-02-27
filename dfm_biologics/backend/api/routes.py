"""
FastAPI routes for construct scoring and blueprint generation.
"""

from fastapi import APIRouter, HTTPException

from core.models import (
    CandidateSpec,
    GateResult,
    ConstructBlueprint,
    HealthResponse,
    ScoringRequest,
)
from core.scoring import ManufacturabilityScoringEngine
from core.checks_construct import ConstructChecker
from core.checks_sequence import SequenceChecker

router = APIRouter()
scoring_engine = ManufacturabilityScoringEngine()


@router.get("/health", response_model=HealthResponse)
async def health_check() -> HealthResponse:
    """
    Health check endpoint.
    """
    return HealthResponse(
        status="ok",
        version="1.0.0"
    )


@router.post("/score", response_model=GateResult)
async def score_construct(request: ScoringRequest) -> GateResult:
    """
    Score a construct candidate for manufacturability.

    **Request:**
    ```json
    {
      "candidate_spec": {
        "project_name": "HER2-bispecific",
        "modality": "IgG_like_bispecific",
        "targets": ["HER2"],
        "expression_system": "mammalian",
        "sequence_type": "protein",
        "sequence": "MVHLTPEEKS...",
        "notes": "Design A"
      },
      "manufacturing_constraints": {
        "max_fragment_length": 500,
        "gc_min": 0.3,
        "gc_max": 0.7,
        "max_homopolymer": 6,
        "forbidden_motifs": [],
        "restriction_sites_to_avoid": [],
        "vendor_profile": "generic"
      }
    }
    ```

    **Response:**
    - `overall_score` (0–100): Composite manufacturability score
    - `sub_scores`: Individual scores for sequence, assembly, developability, expression
    - `flags`: List of issues with locations and severity
    - `suggestions`: High-level design recommendations (no lab protocols)
    - `artifacts`: Normalized FASTA, JSON summary, markdown report
    """
    try:
        result = scoring_engine.score(request.candidate_spec, request.manufacturing_constraints)
        return result
    except ValueError as e:
        raise HTTPException(status_code=400, detail=f"Validation error: {str(e)}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Scoring error: {str(e)}")


@router.post("/blueprint", response_model=ConstructBlueprint)
async def generate_blueprint(candidate_spec: CandidateSpec) -> ConstructBlueprint:
    """
    Generate an abstract construct blueprint (NOT lab assembly steps).

    **Request:**
    ```json
    {
      "project_name": "HER2-bispecific",
      "modality": "IgG_like_bispecific",
      "targets": ["HER2"],
      "expression_system": "mammalian",
      "sequence_type": "protein",
      "sequence": "MVHLTPEEKS...",
      "notes": "Design A"
    }
    ```

    **Response:**
    - `chains`: List of chain identifiers (e.g., [HC1, LC1, HC2, LC2])
    - `domains`: List of domain definitions with chain, name, and optional positions
    - `warnings`: Design-level warnings
    """
    try:
        blueprint = ConstructChecker.generate_blueprint(
            candidate_spec.project_name,
            candidate_spec.modality,
            candidate_spec.sequence,
            candidate_spec.expression_system
        )
        return blueprint
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Blueprint generation error: {str(e)}")
