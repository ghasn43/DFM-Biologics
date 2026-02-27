# CONTRIBUTING

Thank you for your interest in contributing to DFM Biologics!

## Code of Conduct

All contributors must adhere to responsible biotech innovation principles:
- **Safety first:** This tool must never enable harmful bioengineering
- **Transparency:** Features are for computational planning, not wet-lab instructions
- **Compliance:** All work respects biosafety and regulatory requirements
- **Respect:** Inclusive and welcoming community

## Contribution Guidelines

### Developing a Feature

1. **Fork or branch:**
   ```bash
   git checkout -b feature/my-new-feature
   ```

2. **Follow code style:**
   ```bash
   black backend/ app_ui/
   flake8 backend/
   mypy backend/
   ```

3. **Write tests:**
   - Unit tests in `tests/` directory
   - Minimum 80% coverage for new code
   - Test both success and failure cases

4. **Test manually:**
   - Run `pytest tests/ -v`
   - Test UI interactions in Streamlit
   - Verify API docs in FastAPI

5. **Update documentation:**
   - Add docstrings to functions
   - Update README if adding new features
   - Add migration notes if breaking changes

6. **Commit with clear messages:**
   ```bash
   git commit -m "feat: add new scoring metric for X"
   ```

### Types of Contributions

#### 🐛 Bug Fixes
- Identify bug (include reproducible example)
- Fix with minimal changes
- Add regression test

#### ✨ New Features
- Discuss scope first (open an issue)
- Implement with full tests
- Add Streamlit UI integration if user-facing
- Update API docs

#### 📚 Documentation
- Improve clarity of existing docs
- Add examples or tutorials
- Fix typos/links

#### ♻️ Refactoring
- Improve code quality without changing behavior
- Maintain test coverage
- No API changes without feature branch

### PR Process

1. **Create pull request** with description of changes
2. **Link to issue** (if applicable)
3. **Include tests** and coverage report
4. **Pass all checks:**
   - Tests pass: `pytest tests/`
   - Code style: `black` + `flake8`
   - No import errors
5. **Request review** from maintainers

### Commit Message Format

```
type(scope): subject

body

footer
```

**Types:**
- `feat`: New feature
- `fix`: Bug fix
- `docs`: Documentation
- `refactor`: Code refactoring
- `test`: Test additions
- `chore`: Build/tooling

**Example:**
```
feat(scoring): add homopolymer detection weighting

- Multiply homopolymer penalty by length/max_length
- Add gradient scoring (5-15 points)
- Add tests for scoring consistency

Fixes #42
```

### Testing Requirements

**All new code must have tests:**

```python
def test_new_feature():
    """Test description."""
    # Arrange
    input_data = {...}
    
    # Act
    result = function_under_test(input_data)
    
    # Assert
    assert result == expected_output
```

**Run tests before committing:**
```bash
pytest tests/ -v --cov=backend
```

### Code Style

- **Format:** Black (100 char line)
- **Linting:** Flake8
- **Type hints:** Use throughout
- **Docstrings:** Google style

```python
def score_construct(
    candidate: CandidateSpec,
    constraints: ManufacturingConstraints
) -> GateResult:
    """
    Score a construct candidate.
    
    Args:
        candidate: Input construct specification
        constraints: Manufacturing constraints to apply
    
    Returns:
        GateResult with overall and sub-scores
    
    Example:
        >>> result = score_construct(my_spec, my_constraints)
        >>> print(result.overall_score)
    """
    pass
```

### Documentation

- **README.md:** For user-facing overview
- **SETUP.md:** For development setup
- **Docstrings:** In all functions
- **Type hints:** For parameter clarity
- **Comments:** For non-obvious logic

### Safety & Compliance

**Before submitting:**

1. **Verify no lab protocols:** Code should never provide experimental instructions
2. **Check disclaimers:** UI pages include safety notices
3. **Review for misuse:** Could this feature enable harmful use? If yes, reconsider.
4. **Test edge cases:** Ensure robust error handling

### Windows vs Linux

Test on both:
```bash
# Windows
python -m pytest tests/

# Linux/macOS
python3 -m pytest tests/
```

Path handling must work cross-platform.

---

## Quick Start for Contributors

```bash
# 1. Clone repo
git clone <repo-url>
cd dfm_biologics

# 2. Create venv
python -m venv venv
source venv/bin/activate  # or venv\Scripts\activate

# 3. Install dev dependencies
pip install -e ".[dev]"

# 4. Create branch
git checkout -b fix/issue-name

# 5. Make changes + tests

# 6. Test everything
pytest tests/ -v
black backend/
flake8 backend/

# 7. Commit
git commit -m "fix: description"

# 8. Push & create PR
git push origin fix/issue-name
```

---

## Issue Templates

### Bug Report
```markdown
**Describe the bug:**
What happened?

**Reproduce:**
Steps to reproduce the issue

**Expected behavior:**
What should happen?

**Environment:**
- OS: [Windows/macOS/Linux]
- Python: [version]
- Installed from: [pip/git]
```

### Feature Request
```markdown
**Is your feature related to a problem?**
Describe the use case

**Solution you'd like:**
How should this work?

**Alternatives considered:**
Other approaches?

**Safety review:**
Could this enable harmful use?
```

---

## Recognition

Contributors will be recognized in:
- README.md contributors section
- Release notes
- GitHub contributors page

---

Thank you for helping make DFM Biologics safer and more useful! 🙏

**Before contributing, please read:**
- LICENSE (MIT + responsible use agreement)
- README.md (safety notices)
- SETUP.md (development guide)
