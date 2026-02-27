# SETUP & DEVELOPMENT GUIDE

## System Requirements

- **Python:** 3.11 or later
- **OS:** Windows, macOS, Linux
- **Disk Space:** ~500 MB (including virtual environment)
- **RAM:** 2 GB minimum

## Installation Steps

### 1. Clone or Extract the Repository

```bash
cd dfm_biologics
```

### 2. Create Virtual Environment

**Windows:**
```bash
python -m venv venv
venv\Scripts\activate
```

**macOS/Linux:**
```bash
python3 -m venv venv
source venv/bin/activate
```

### 3. Install Packages

```bash
pip install -e .
```

Install development packages (optional, for testing/linting):
```bash
pip install -e ".[dev]"
```

### 4. Verify Installation

```bash
python -c "from backend.core.models import CandidateSpec; print('✅ Backend imports OK')"
streamlit --version
```

---

## Running the Application

### Terminal 1: Start Backend (FastAPI)

```bash
cd backend
python main.py
```

You should see:
```
🧬 DFM Biologics Backend
🚀 Starting on 127.0.0.1:8000
📖 API Docs: http://127.0.0.1:8000/docs
```

**Access:**
- API Docs (interactive): http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc
- Health: http://localhost:8000/health

### Terminal 2: Start Frontend (Streamlit)

In a **new terminal window**:

```bash
cd /path/to/dfm_biologics
streamlit run app_ui/streamlit_app.py
```

You should see:
```
  You can now view your Streamlit app in your browser.

  Local URL: http://localhost:8501
```

**Access:** http://localhost:8501

---

## Running Tests

### Run All Tests

```bash
pytest tests/ -v
```

### Run Specific Test File

```bash
pytest tests/test_scoring.py -v
pytest tests/test_checks.py -v
```

### Run with Coverage Report

```bash
pytest tests/ --cov=backend --cov-report=html
```

Then open `htmlcov/index.html` to view coverage.

---

## Configuration

Create a `.env` file from the template:

```bash
cp .env.example .env
```

Default values work for local development. Edit as needed:

```env
BACKEND_HOST=127.0.0.1
BACKEND_PORT=8000
LOG_LEVEL=INFO
DEBUG=false
```

---

## Project Structure Explanation

```
dfm_biologics/
├── backend/                       # FastAPI backend
│   ├── main.py                   # Entry point
│   ├── api/
│   │   └── routes.py             # API endpoints (/score, /blueprint, /health)
│   ├── core/
│   │   ├── models.py             # Pydantic schemas (input/output types)
│   │   ├── scoring.py            # Core scoring logic
│   │   ├── checks_sequence.py    # Sequence analysis (GC, repeats, etc.)
│   │   ├── checks_construct.py   # Construct blueprint generation
│   │   ├── report.py             # Report generation
│   │   └── utils.py              # Helper functions
│   └── data/
│       ├── codon_tables.json     # Codon usage reference
│       └── vendor_rules.yaml     # Vendor constraints
├── app_ui/                        # Streamlit frontend
│   ├── streamlit_app.py          # Main UI page
│   └── pages/
│       ├── 1_Candidate_Input.py  # Input form + scoring
│       ├── 2_Construct_Architecture.py  # Blueprint viewer
│       └── 3_Manufacturability_Report.py  # Results viewer
├── tests/                         # Unit tests
│   ├── test_scoring.py           # Scoring logic tests
│   └── test_checks.py            # Sequence/construct check tests
├── pyproject.toml                # Package metadata
├── .env.example                  # Environment template
├── .gitignore                    # Git exclusions
└── README.md                     # Main documentation
```

---

## Common Commands

| Task | Command |
|------|---------|
| Install dependencies | `pip install -e .` |
| Install dev tools | `pip install -e ".[dev]"` |
| Start backend | `cd backend && python main.py` |
| Start frontend | `streamlit run app_ui/streamlit_app.py` |
| Run tests | `pytest tests/ -v` |
| Format code | `black backend/ app_ui/ tests/` |
| Lint code | `flake8 backend/ app_ui/ tests/` |
| Type check | `mypy backend/` |

---

## Troubleshooting

### Backend won't start
- **Error:** `Address already in use`
  - Another process is on port 8000. Kill it or change `BACKEND_PORT` in `.env`

### Frontend can't connect to backend
- **Error:** `Backend not reachable`
  - Ensure FastAPI is running on localhost:8000
  - Check firewall/antivirus settings

### Tests fail
- Ensure all packages installed: `pip install -e ".[dev]"`
- Clear pytest cache: `rm -rf .pytest_cache/`

### Import errors
- Verify virtual environment is activated
- Reinstall: `pip install -e .`

---

## Development Workflow

1. **Activate venv:**
   ```bash
   source venv/bin/activate  # or venv\Scripts\activate on Windows
   ```

2. **Make code changes**

3. **Run tests:**
   ```bash
   pytest tests/ -v
   ```

4. **Format & lint:**
   ```bash
   black backend/ app_ui/ tests/
   flake8 backend/
   ```

5. **Test manually:**
   - Start backend: `cd backend && python main.py`
   - Start frontend: `streamlit run app_ui/streamlit_app.py`
   - Test workflows in UI

---

## Adding New Features

### New Scoring Metric

1. Add to `backend/core/scoring.py`
2. Add tests in `tests/test_scoring.py`
3. Update models in `backend/core/models.py` if needed
4. Add UI elements in `app_ui/pages/3_Manufacturability_Report.py`

### New Construct Check

1. Add function to `backend/core/checks_sequence.py` or `checks_construct.py`
2. Add unit tests in `tests/test_checks.py`
3. Integrate into `scoring.py` scoring logic
4. Test via Streamlit

### New Frontend Page

1. Create `app_ui/pages/X_PageName.py`
2. Add imports for session state from main page
3. Test via Streamlit (auto-loads)

---

## Performance Considerations

- Scoring a 1000 bp sequence: ~50 ms
- Full report generation: ~100 ms
- Streamlit pages load ~1–2 seconds

For large projects, consider:
- Caching results in session state (already done)
- Async processing for multiple sequences

---

## Safety & Compliance

- **All output is for computational planning only**
- **No wet-lab protocols are provided**
- **All designs must be reviewed by experts**
- **Comply with biosafety regulations**
- **Adhere to DURC policies**

See LICENSE and README for full compliance information.

---

## Getting Help

- Check README.md for API documentation
- Review test files for usage examples
- Check Streamlit/FastAPI documentation:
  - https://streamlit.io/docs
  - https://fastapi.tiangolo.com/

---

**Happy designing! 🧬**
