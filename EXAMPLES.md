# EXAMPLES & QUICK START

This guide shows how to use DFM Biologics with practical examples.

---

## Table of Contents

1. [Quick Start (5 minutes)](#quick-start)
2. [API Examples](#api-examples)
3. [Streamlit UI Walkthrough](#streamlit-ui-walkthrough)
4. [Common Use Cases](#common-use-cases)
5. [Troubleshooting](#troubleshooting)

---

## Quick Start

### Setup (First Time)

```bash
# 1. Create virtual environment
python -m venv venv
venv\Scripts\activate              # Windows
# or
source venv/bin/activate           # macOS/Linux

# 2. Install packages
pip install -e .

# 3. Start backend (Terminal 1)
cd backend
python main.py

# 4. Start frontend (Terminal 2)
cd ..
streamlit run app_ui/streamlit_app.py

# 5. Open browser
# http://localhost:8501
```

### First Analysis (2 minutes)

1. Go to **Candidate Input** page
2. Enter:
   - **Project Name:** `HER2-001`
   - **Modality:** `VHH_bispecific`
   - **Expression System:** `mammalian`
   - **Sequence:**
     ```
     MVHLTPEEKSLIPQPPGGGGAAA
     ```
3. Click **Score Construct**
4. Go to **Manufacturability Report** to see results

---

## API Examples

### Using `curl`

#### Example 1: Score a Simple Bispecific

```bash
curl -X POST "http://localhost:8000/score" \
  -H "Content-Type: application/json" \
  -d '{
    "candidate_spec": {
      "project_name": "test-vhh-001",
      "modality": "VHH_bispecific",
      "targets": ["HER2", "HER3"],
      "expression_system": "mammalian",
      "sequence_type": "protein",
      "sequence": "MVHLTPEEKSLIPQPPGAAA",
      "notes": "Bispecific targeting HER2 and HER3"
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

**Response:**
```json
{
  "overall_score": 78,
  "sub_scores": {
    "sequence_synth": 82,
    "assembly_risk": 75,
    "developability": 80,
    "expression_risk": 72
  },
  "flags": [
    {
      "severity": "info",
      "category": "general",
      "message": "Large construct may reduce expression levels",
      "location": null
    }
  ],
  "suggestions": [
    "Construct appears well-optimized; proceed with experimental validation"
  ],
  "artifacts": {
    "normalized_fasta": ">test-vhh-001\nMVHLTPEEKSLIPQPPGAAA\n",
    "json_summary": {...},
    "markdown_report": "# Manufacturability Report..."
  }
}
```

#### Example 2: Get Blueprint

```bash
curl -X POST "http://localhost:8000/blueprint" \
  -H "Content-Type: application/json" \
  -d '{
    "project_name": "igg-bispecific-001",
    "modality": "IgG_like_bispecific",
    "targets": ["HER2"],
    "expression_system": "mammalian",
    "sequence_type": "protein",
    "sequence": "MVHLTPEEKSLIPQPPGAAAVHLTPEEKSLIPQPPGAAAVHLTPEEKSLIPQPPGAAAVHLTPEEKSLIPQPPGAAA",
    "notes": "IgG bispecific"
  }'
```

**Response:**
```json
{
  "chains": ["HC1", "LC1", "HC2", "LC2"],
  "domains": [
    {"chain": "HC1", "name": "VH1", "start": null, "end": null},
    {"chain": "HC1", "name": "CH1", "start": null, "end": null},
    {"chain": "LC1", "name": "VL1", "start": null, "end": null},
    {"chain": "LC1", "name": "CL", "start": null, "end": null},
    {"chain": "HC2", "name": "VH2", "start": null, "end": null},
    {"chain": "HC2", "name": "CH1", "start": null, "end": null},
    {"chain": "LC2", "name": "VL2", "start": null, "end": null},
    {"chain": "LC2", "name": "CL", "start": null, "end": null}
  ],
  "warnings": []
}
```

#### Example 3: Health Check

```bash
curl "http://localhost:8000/health"
```

**Response:**
```json
{
  "status": "ok",
  "version": "1.0.0"
}
```

### Using Python Requests

```python
import requests
import json

BASE_URL = "http://localhost:8000"

# 1. Check health
response = requests.get(f"{BASE_URL}/health")
print(response.json())
# {'status': 'ok', 'version': '1.0.0'}

# 2. Score a construct
payload = {
    "candidate_spec": {
        "project_name": "my-construct",
        "modality": "VHH_bispecific",
        "targets": ["EGFR"],
        "expression_system": "mammalian",
        "sequence_type": "protein",
        "sequence": "MVHLTPEEKSLIPQPPGAAA",
        "notes": "Test construct"
    },
    "manufacturing_constraints": {
        "max_fragment_length": 500,
        "gc_min": 0.3,
        "gc_max": 0.7,
        "max_homopolymer": 6,
        "forbidden_motifs": ["AAAA"],
        "restriction_sites_to_avoid": ["EcoRI"],
        "vendor_profile": "generic"
    }
}

response = requests.post(f"{BASE_URL}/score", json=payload)
result = response.json()

print(f"Score: {result['overall_score']}/100")
print(f"Flags: {len(result['flags'])}")
for flag in result['flags']:
    print(f"  - {flag['severity']}: {flag['message']}")

# 3. Get blueprint
payload = {
    "project_name": "my-construct",
    "modality": "Fab_scFv",
    "targets": ["PD-L1"],
    "expression_system": "mammalian",
    "sequence_type": "protein",
    "sequence": "MVHLTPEEKSLIPQPPGAAAVHLTPEEKSLIPQPPGAAA",
    "notes": "Fab-scFv hybrid"
}

response = requests.post(f"{BASE_URL}/blueprint", json=payload)
blueprint = response.json()

print(f"Chains: {blueprint['chains']}")
print(f"Domains: {len(blueprint['domains'])}")
for warning in blueprint['warnings']:
    print(f"  Warning: {warning}")
```

---

## Streamlit UI Walkthrough

### Page 1: Candidate Input

**What to do:**

1. **Fill out project info:**
   - Project Name: `HER2-VHH-fusion-v2`
   - Modality: `VHH_bispecific`
   - Targets: Select `HER2` (or type custom)
   - Expression System: `mammalian`

2. **Enter sequence** (supports FASTA):
   ```
   >my_vhh_bispecific
   MVHLTPEEKSLIPQPPGAAAVHLTPEEKSLIPQPPGAAAVHLTPEEKSLIPQPPGAAA
   ```

3. **Set constraints** (optional):
   - Max Fragment Length: 500
   - GC Min: 30%, GC Max: 70%
   - Max Homopolymer: 6
   - Forbidden Motifs: `AAAA,GGGG` (comma-separated)
   - Restriction Sites: `EcoRI,BamHI`

4. **Click buttons:**
   - **Generate Blueprint** → See architecture (Page 2)
   - **Score Construct** → Get scoring results (Page 3)

### Page 2: Construct Architecture

**What you'll see:**

- **Blueprint Summary**: Chain list and domain count
- **Architecture Diagram**: Visual representation of your modality
- **Domain Table**: Each domain with chain, name, and position
- **Warnings**: Design-level concerns
- **Export Options**: Download as JSON or Markdown

**Example output for IgG bispecific:**
```
HC1 ┓
    ├─ IgG 1
LC1 ┛

HC2 ┓
    ├─ IgG 2 (different specificity)
LC2 ┛
```

### Page 3: Manufacturability Report

**What you'll see:**

1. **Score Summary** (big metrics):
   - Overall Score: 78/100 🟢
   - Sequence Synth: 82
   - Assembly Risk: 75
   - Developability: 80
   - Expression Risk: 72

2. **Flags Table** (filterable by severity):
   - ❌ Errors (must address)
   - ⚠️ Warnings (should address)
   - ℹ️ Info messages (for awareness)

3. **Recommendations**:
   - High-level design suggestions
   - **No wet-lab protocols provided**

4. **Export**:
   - Download Markdown report
   - Download JSON summary
   - Download full results

---

## Common Use Cases

### Use Case 1: Optimize a VHH Bispecific

**Goal:** Design a compact bispecific antibody for cancer immunotherapy

**Steps:**

1. **Start with reference:** Get a known VHH sequence (e.g., camelid vs human)
2. **Design linker:** Try different linker lengths (15–30 aa typical)
3. **Score iteratively:**
   - Initial sequence → Score → Review flags
   - Modify based on feedback → Score again
   - Track iterations
4. **Export final:** Download report for your team

**Example sequences:**
```
# VHH1 (camelid-like)
EVQLVESGGGLVQPKGSLRLSCAASGFTFSNYGVHWVRQAPGKGLEWVGFISQSGNKITYADSVKGRFTISADAQNSLYLQMNSLKLPDTAVYYCNVRHPPYYWQSWGATVTVSS

# Linker (GGGS repeat - flexible)
GGGSGGGSGGGSGGGSGGGSGGGSGGGSGGGSGGGSGGGSGGGSGGGSGGGSGGGSGGGSGGGSGGGSGGGSGGGSGGGSGGGSGGGSGGGSGGGSGGGSGGGSGGGSGGGSGG

# VHH2 (human-like)
QVQLVQSGAEVKKPGASVKVSCKASGYTFTSNYGVHWVRQTPGKGLEWIGFISPSGSNITYADSVKGRFTISRDNAKSLYLQMNNLKPEDTAVYYCNVRHPPYYWQQSSQGKTG
```

### Use Case 2: Compare Expression Systems

**Goal:** Find best expression system for your construct

**Steps:**

1. **Score once for each system:**
   - Mammalian
   - Yeast
   - E. coli
   - Cell-free

2. **Compare Expression Risk scores**
3. **Note warnings** for each system
4. **Choose based on:**
   - Lowest risk
   - Lab capacity
   - Timeline

### Use Case 3: Design Fab-scFv Hybrid

**Goal:** Create hybrid antibody format for dual targeting

**Steps:**

1. **Use architecture page** to understand Fab-scFv layout:
   - Fab (fixed): HC + LC with constant domains
   - scFv (variable): Single-chain Fv construct

2. **Score with constraints:**
   - Max length: 600 aa (larger format)
   - GC windows: Avoid extreme regions
   - Forbidden: Custom linker patterns

3. **Address assembly warnings:**
   - Will have >3 fragments
   - Consider modular manufacturing

4. **Export blueprint** for wet-lab team

### Use Case 4: Flag-Driven Design Iteration

**Goal:** Reduce flags (improve manufacturability)

**Workflow:**

```
Iteration 1:
- Score construct
- See 5 warnings, 2 errors
- Identify: homopolymer runs, high GC window

Iteration 2:
- Edit sequence to avoid homopolymers
- Reduce GC in high region
- Score again
- See 2 warnings, 0 errors ✓

Iteration 3:
- Optional refinement
- Add optimized linker
- Final score: 85/100 🟢

→ Ready for experimental validation!
```

---

## Troubleshooting

### Problem: "Backend not reachable"

**Solution:**
```bash
# Terminal 1: Check backend is running
cd backend
python main.py

# Terminal 2: Test health
curl http://localhost:8000/health
```

### Problem: "importError: No module named 'backend'"

**Solution:**
```bash
# Make sure you're in the right directory
cd dfm_biologics

# Reinstall with -e (editable)
pip install -e .
```

### Problem: "Streamlit can't find pages"

**Solution:**
```bash
# Run from the repo root, not from app_ui/
cd dfm_biologics
streamlit run app_ui/streamlit_app.py
```

### Problem: Tests fail with "ModuleNotFoundError"

**Solution:**
```bash
# Install dev dependencies
pip install -e ".[dev]"

# Run from repo root
cd dfm_biologics
pytest tests/ -v
```

### Problem: "Address already in use" for port 8000

**Solution:**
```bash
# Change port in .env
BACKEND_PORT=8001

# Or kill process using port 8000
# On Windows:
netstat -ano | findstr :8000
taskkill /PID <PID> /F

# On macOS/Linux:
lsof -ti:8000 | xargs kill -9
```

---

## Tips & Tricks

### Batch Scoring (Advanced)

```python
import requests
import json

sequences = [
    "MVHLTPEEKSLIPQPPGAAA",
    "MVHLTPEEKSLIPQPPGGGG",
    "MVHLTPEEKSLIPQPPAAAA",
]

results = []

for i, seq in enumerate(sequences, 1):
    payload = {
        "candidate_spec": {..., "project_name": f"batch-{i}", "sequence": seq},
        "manufacturing_constraints": {...}
    }
    
    response = requests.post("http://localhost:8000/score", json=payload)
    results.append(response.json())

# Analyze results
for result in results:
    print(f"{result['artifacts']['json_summary']['project']}: {result['overall_score']}/100")
```

### Export Automation

```bash
# Batch export to files
for i in {1..10}; do
    curl -s -X POST "http://localhost:8000/score" \
      -H "Content-Type: application/json" \
      -d "{...}" | jq '.artifacts.markdown_report' > report_$i.md
done
```

### Reproducible Results

```python
# Same input = Same output (deterministic)
result1 = requests.post(..., json=payload).json()
result2 = requests.post(..., json=payload).json()

assert result1['overall_score'] == result2['overall_score']
assert result1['artifacts']['normalized_fasta'] == result2['artifacts']['normalized_fasta']
```

---

## Next Steps

- ✅ Run first scoring (see Quick Start)
- 📖 Read [README.md](README.md) for API details
- 🔧 Review [SETUP.md](SETUP.md) for development
- 🧪 Explore test examples in [tests/](tests/)
- 💡 Try different modalities and expression systems
- 🤝 Share feedback!

---

**Questions?** Check the README or SETUP guide. Happy designing! 🧬
