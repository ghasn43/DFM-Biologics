# DFM Biologics: Construct Builder & Manufacturability Gate

A SAFE, non-operational in-silico tool for biotech construct planning, manufacturability scoring, and documentation. This app **does NOT provide wet-lab instructions** and is designed to support early-stage computational design and risk assessment only.

## ⚠️ Safety Notice

**This tool is for computational planning and risk flagging only.** It:
- ✅ Analyzes sequence properties (GC content, repeats, motifs)
- ✅ Generates abstract construct blueprints
- ✅ Scores manufacturability and developability risks
- ✅ Suggests high-level design improvements
- ❌ Does NOT provide step-by-step wet-lab protocols
- ❌ Does NOT replace experimental validation or expert review
- ❌ Must NOT be used for harmful bioengineering

All designs must be validated by qualified molecular biologists and comply with all applicable regulations.

---

## Quick Start

### Prerequisites
- Python 3.11+
- pip or conda

### Installation

1. **Clone or extract the repository**
   ```bash
   cd dfm_biologics
   ```

2. **Create a virtual environment**
   ```bash
   python -m venv venv
   source venv/bin/activate          # Linux/Mac
   # or
   venv\Scripts\activate              # Windows
   ```

3. **Install dependencies**
   ```bash
   pip install -e .
   ```

### Run Backend (FastAPI)

```bash
cd backend
python main.py
```

Backend runs on `http://localhost:8000`
- **API Docs**: `http://localhost:8000/docs`
- **ReDoc**: `http://localhost:8000/redoc`

### Run Frontend (Streamlit)

In a new terminal:
```bash
streamlit run app_ui/streamlit_app.py
```

Frontend runs on `http://localhost:8501`

---

## Project Structure

```
dfm_biologics/
├── README.md
├── pyproject.toml
├── .env.example
├── app_ui/
│   ├── streamlit_app.py           (main UI entry point)
│   └── pages/
│       ├── 1_Candidate_Input.py    (sequence & modality input)
│       ├── 2_Construct_Architecture.py  (blueprint visualization)
│       └── 3_Manufacturability_Report.py (scores & export)
├── backend/
│   ├── main.py                     (FastAPI app)
│   ├── api/
│   │   └── routes.py               (POST /score, POST /blueprint, GET /health)
│   ├── core/
│   │   ├── models.py               (Pydantic schemas: CandidateSpec, GateResult, etc.)
│   │   ├── scoring.py              (scoring engine & logic)
│   │   ├── checks_sequence.py       (FASTA parsing, GC, homopolymers, repeats)
│   │   ├── checks_construct.py      (modality → blueprint mapping)
│   │   ├── report.py                (report generation)
│   │   └── utils.py                 (helpers)
│   └── data/
│       ├── codon_tables.json        (minimal codon usage reference)
│       └── vendor_rules.yaml        (placeholder vendor constraints)
├── tests/
│   ├── test_scoring.py              (unit tests for scoring)
│   └── test_checks.py               (unit tests for sequence/construct checks)
```

---

## API Endpoints

### Base URL
```
http://localhost:8000
```

### 1. POST `/score`

**Score a construct for manufacturability.**

Request:
```json
{
  "candidate_spec": {
    "project_name": "HER2-VHH-fusion",
    "modality": "VHH_bispecific",
    "targets": ["HER2", "HER3"],
    "expression_system": "mammalian",
    "sequence_type": "protein",
    "sequence": "MVHLTPEEKS",
    "notes": "Test candidate"
  },
  "manufacturing_constraints": {
    "max_fragment_length": 500,
    "gc_min": 0.3,
    "gc_max": 0.7,
    "max_homopolymer": 6,
    "forbidden_motifs": ["AAAA", "GGGG"],
    "restriction_sites_to_avoid": ["EcoRI", "BamHI"],
    "vendor_profile": "generic"
  }
}
```

Response:
```json
{
  "overall_score": 72,
  "sub_scores": {
    "sequence_synth": 75,
    "assembly_risk": 68,
    "developability": 72,
    "expression_risk": 75
  },
  "flags": [
    {
      "severity": "warning",
      "category": "homopolymer",
      "message": "Homopolymer VH found at position 10–14, length 5 (threshold 6)",
      "location": [10, 14]
    }
  ],
  "suggestions": [
    "Consider reducing long homopolymer stretches to <6 consecutive bases",
    "Review linker length for optimal expression in mammalian systems"
  ],
  "artifacts": {
    "normalized_fasta": ">project|HER2-VHH-fusion\nMVHLTPEEKS\n",
    "json_summary": {...},
    "markdown_report": "# Manufacturability Report\n..."
  }
}
```

### 2. POST `/blueprint`

**Generate an abstract construct blueprint.**

Request:
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

Response:
```json
{
  "chains": ["HC1", "LC1", "HC2", "LC2"],
  "domains": [
    {"chain": "HC1", "name": "VH1", "start": 0, "end": 120},
    {"chain": "HC1", "name": "CH1", "start": 121, "end": 200}
  ],
  "warnings": [
    "Long HC2 may require linker optimization"
  ]
}
```

### 3. GET `/health`

**Health check.**

Response:
```json
{
  "status": "ok",
  "version": "1.0.0"
}
```

---

## Example cURL Requests

### Score a construct:
```bash
curl -X POST "http://localhost:8000/score" \
  -H "Content-Type: application/json" \
  -d '{
    "candidate_spec": {
      "project_name": "test-001",
      "modality": "VHH_bispecific",
      "targets": ["HER2"],
      "expression_system": "mammalian",
      "sequence_type": "protein",
      "sequence": "MVHLTPEEKSLIP",
      "notes": "Test"
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
  }'
```

### Get blueprint:
```bash
curl -X POST "http://localhost:8000/blueprint" \
  -H "Content-Type: application/json" \
  -d '{
    "project_name": "test-001",
    "modality": "VHH_bispecific",
    "targets": ["HER2"],
    "expression_system": "mammalian",
    "sequence_type": "protein",
    "sequence": "MVHLTPEEKSLIP",
    "notes": "Test"
  }'
```

### Health check:
```bash
curl "http://localhost:8000/health"
```

---

## Testing

Run all tests:
```bash
pytest tests/ -v
```

Run specific test file:
```bash
pytest tests/test_scoring.py -v
```

Run with coverage:
```bash
pytest tests/ --cov=backend --cov-report=html
```

---

## Configuration

Create a `.env` file based on `.env.example`:

```bash
cp .env.example .env
```

Customize if needed (e.g., backend port, log level). Defaults work out-of-the-box.

---

## Supported Modalities

| Modality | Array | Chains | Example Use |
|----------|-------|--------|-------------|
| `IgG_like_bispecific` | 2×2 | HC1, LC1, HC2, LC2 (+ Fc) | Dual-targeting antibody |
| `VHH_bispecific` | Paired | [VHH1–Linker–VHH2] | Single-chain, small format |
| `Fab_scFv` | Hybrid | [Fab + scFv] | Fab + single-chain |
| `Fc_fusion` | Fusion | [Binder + Fc] | Fusion protein |

---

## Supported Expression Systems

- `mammalian` — CHO, HEK293, etc.
- `yeast` — P. pastoris, S. cerevisiae
- `ecoli` — E. coli (non-glycosylated)
- `cell_free` — In vitro cell-free systems

---

## Scoring Methodology

### Overall Score: 0–100

Composite of four sub-scores:

1. **Sequence Synthesis (0–100)**
   - GC content window deviation
   - Homopolymer presence
   - Presence of repeats
   - Palindrome/hairpin risk (proxy)
   - Forbidden motifs

2. **Assembly Risk (0–100)**
   - Number of fragments (modality-derived)
   - Linker presence/length heuristic
   - Sequence complexity

3. **Developability (0–100)**
   - Glycosylation risk sites (NXST)
   - Deamidation hotspots (NG, NS, NT)
   - Oxidation-prone M residues
   - Proteolytic cleavage motifs (basic pairs)

4. **Expression Risk (0–100)**
   - System-specific liabilities (e.g., mammalian codon bias)
   - Construct complexity
   - Size heuristics

All penalties generate flags with locations for full explainability.

---

## Next Enhancements

- **Vendor Profiles**: Full Twist, IDT, Geneious integration profiles
- **Secondary Structure Estimation**: MFold or RNAfold integration (with safety gates)
- **PDF Export**: Comprehensive report generation
- **Glycosylation Mapping**: Detailed NXST analysis with severity levels
- **Codon Optimization**: Per-expression-system codon bias tables
- **Design History**: Project versioning and comparison
- **Regulatory Compliance Checks**: GLP/cGMP-aligned audit trail
- **Machine Learning Scoring**: ML-based developability prediction (with transparency)
- **Sequence Alignment**: BLAST-like motif search (safe, read-only)
- **Docker Deployment**: Containerized backend and UI

---

## Contributing & Compliance

This project is designed for research and design planning only. Before using outputs for manufacturing or clinical applications:

1. ✅ Obtain expert molecular biologist review
2. ✅ Perform experimental validation
3. ✅ Comply with institutional biosafety and regulatory requirements
4. ✅ Ensure adherence to dual-use research of concern (DURC) policies

---

## License

Academic/Research Use (specify license in LICENSE file)

---

## Support & Questions

For questions or issues, consult your biotech team lead or institutional biosafety committee.

---

**Built with safety-first principles for responsible biotech innovation.**
