# Contributing Guide

Thank you for your interest in improving the Restaurant Reservation AI Agent! This guide will help you contribute effectively.

---

## Development Setup

### Prerequisites
- Python 3.9+
- Git
- Groq API key
- Code editor (VS Code recommended)

### Initial Setup
```bash
# Fork and clone repository
git clone <your-fork-url>
cd restaurant-reservation-agent

# Create virtual environment
python -m venv venv
source venv/bin/activate  # or venv\Scripts\activate on Windows

# Install dependencies
pip install -r requirements.txt

# Install development dependencies
pip install pytest black flake8 mypy

# Create .env file
cp .env.example .env
# Add your GROQ_API_KEY

# Generate test data
python data/generator.py
```

---

## Code Style

### Python Style Guide
We follow PEP 8 with these specifics:

```python
# Use type hints
def process_message(user_message: str, user_name: str) -> str:
    pass

# Docstrings for all public functions
def execute(self, args: Dict) -> Dict:
    """
    Execute the tool with given arguments.
    
    Args:
        args: Dictionary containing tool parameters
        
    Returns:
        Dictionary with execution results
    """
    pass

# Use descriptive variable names
restaurant_id = 1  # Good
rid = 1  # Bad

# Constants in UPPER_CASE
MAX_HISTORY = 20
DEFAULT_MODEL = "llama-3.3-70b-versatile"
```

### Formatting
```bash
# Format code with black
black .

# Check style with flake8
flake8 .

# Type checking with mypy
mypy agent/ tools/ data/
```

---

## Project Structure

### Adding New Features

#### 1. Adding a New Tool

Create file in `tools/` directory:

```python
# tools/new_tool.py
"""
New Tool Description
Brief explanation of what this tool does
"""

from typing import Dict

class NewTool:
    def __init__(self):
        # Initialize any required resources
        pass
    
    def execute(self, args: Dict) -> Dict:
        """
        Execute the tool
        
        Args:
            arg1: Description
            arg2: Description
        
        Returns:
            Dict with success status and results
        """
        try:
            # Implementation here
            return {
                "success": True,
                "result": "..."
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }
```

Register in `agent/orchestrator.py`:

```python
from tools.new_tool import NewTool

class AgentOrchestrator:
    def __init__(self, ...):
        self.tools = {
            # ... existing tools
            "new_tool": NewTool()
        }
```

Update system prompt in `agent/prompt_manager.py`:

```python
SYSTEM_PROMPT_V5 = """
...
### new_tool
Description of what the tool does
Args:
- arg1: type (description)
- arg2: type (description)
...
"""
```

#### 2. Modifying the Agent

Main agent logic is in `agent/orchestrator.py`:

```python
# To change LLM parameters
response = self.client.chat.completions.create(
    model=self.model_name,
    messages=messages,
    temperature=0.7,  # Adjust for creativity
    max_tokens=1024,  # Adjust for response length
    top_p=0.9
)

# To modify tool routing
def _execute_tools(self, tool_calls: List[Dict]) -> List[Dict]:
    # Add custom logic here
    pass
```

#### 3. Enhancing the UI

Streamlit app is in `frontend/streamlit_app.py`:

```python
# Add new sidebar widget
with st.sidebar:
    if st.button("New Feature"):
        # Implementation
        pass

# Add new page
def new_page():
    st.title("New Feature")
    # Implementation

# Add to navigation
page = st.sidebar.selectbox("Page", ["Chat", "Analytics", "New Feature"])
if page == "New Feature":
    new_page()
```

---

## Testing

### Writing Tests

Add test scenarios to `evaluation/test_scenarios.py`:

```python
{
    "name": "Test New Feature",
    "conversation": [
        {
            "user": "Test query",
            "expected_tools": ["new_tool"],
            "expected_intent": "test"
        }
    ],
    "success_criteria": {
        "feature_works": True
    }
}
```

### Running Tests

```bash
# Run all tests
python evaluation/test_scenarios.py

# Run specific test
python -c "from evaluation.test_scenarios import *; run_specific_test('Test Name')"
```

### Test Coverage Goals
- Intent detection: >90%
- Tool execution: >95%
- Error handling: 100%
- Edge cases: >85%

---

## Database Changes

### Schema Modifications

Edit `data/generator.py`:

```python
# Add new table
cursor.execute('''
    CREATE TABLE IF NOT EXISTS new_table (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        field1 TEXT NOT NULL,
        field2 INTEGER,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
''')

# Add index
cursor.execute('''
    CREATE INDEX idx_new_table_field1 ON new_table(field1)
''')
```

### Data Migration

Create migration script:

```python
# migrations/001_add_new_field.py
import sqlite3

def migrate():
    conn = sqlite3.connect('data/restaurants.db')
    cursor = conn.cursor()
    
    cursor.execute('''
        ALTER TABLE restaurants ADD COLUMN new_field TEXT
    ''')
    
    conn.commit()
    conn.close()

if __name__ == "__main__":
    migrate()
```

---

## Documentation

### Code Documentation

```python
def complex_function(arg1: str, arg2: int) -> Dict:
    """
    Brief one-line description.
    
    Longer description explaining the function's purpose,
    behavior, and any important details.
    
    Args:
        arg1: Description of first argument
        arg2: Description of second argument
    
    Returns:
        Dictionary containing:
        - key1: Description
        - key2: Description
    
    Raises:
        ValueError: When arg2 is negative
        TypeError: When arg1 is not a string
    
    Example:
        >>> result = complex_function("test", 42)
        >>> print(result['key1'])
        'value'
    """
    pass
```

### README Updates

When adding features, update:
- `README.md` - Main documentation
- `QUICKSTART.md` - If setup changes
- `docs/ARCHITECTURE.md` - If architecture changes
- `docs/USE_CASE.md` - If business logic changes

---

## Git Workflow

### Branch Naming

```bash
# Feature branches
git checkout -b feature/add-voice-interface

# Bug fixes
git checkout -b fix/booking-validation

# Documentation
git checkout -b docs/update-architecture

# Refactoring
git checkout -b refactor/optimize-embeddings
```

### Commit Messages

Follow conventional commits:

```bash
# Format: <type>(<scope>): <subject>

# Examples:
git commit -m "feat(tools): add waitlist management tool"
git commit -m "fix(agent): resolve tool parsing error"
git commit -m "docs(readme): update installation instructions"
git commit -m "refactor(db): optimize query performance"
git commit -m "test(evaluation): add edge case scenarios"
```

Types:
- `feat`: New feature
- `fix`: Bug fix
- `docs`: Documentation
- `refactor`: Code refactoring
- `test`: Adding tests
- `perf`: Performance improvement
- `chore`: Maintenance tasks

### Pull Request Process

1. **Create feature branch**
   ```bash
   git checkout -b feature/my-feature
   ```

2. **Make changes and commit**
   ```bash
   git add .
   git commit -m "feat: add my feature"
   ```

3. **Push to your fork**
   ```bash
   git push origin feature/my-feature
   ```

4. **Create Pull Request**
   - Clear title and description
   - Reference any related issues
   - Include screenshots if UI changes
   - List breaking changes if any

5. **PR Template**
   ```markdown
   ## Description
   Brief description of changes
   
   ## Type of Change
   - [ ] Bug fix
   - [ ] New feature
   - [ ] Breaking change
   - [ ] Documentation update
   
   ## Testing
   - [ ] Tests pass locally
   - [ ] Added new tests
   - [ ] Manual testing completed
   
   ## Checklist
   - [ ] Code follows style guidelines
   - [ ] Documentation updated
   - [ ] No breaking changes (or documented)
   ```

---

## Performance Optimization

### Profiling

```python
import cProfile
import pstats

# Profile a function
profiler = cProfile.Profile()
profiler.enable()

# Your code here
result = orchestrator.process_message("test")

profiler.disable()
stats = pstats.Stats(profiler)
stats.sort_stats('cumulative')
stats.print_stats(10)
```

### Optimization Checklist
- [ ] Database queries use indexes
- [ ] Embeddings cached in memory
- [ ] LLM calls minimized
- [ ] Large data structures avoided in loops
- [ ] Async operations where possible

---

## Security

### Security Checklist
- [ ] No API keys in code
- [ ] Input validation on all user inputs
- [ ] SQL injection prevention (parameterized queries)
- [ ] XSS protection (output encoding)
- [ ] Rate limiting implemented
- [ ] Error messages don't leak sensitive info

### Reporting Security Issues

**DO NOT** open public issues for security vulnerabilities.

Instead:
1. Email security concerns privately
2. Include detailed description
3. Provide steps to reproduce
4. Suggest a fix if possible

---

## Release Process

### Version Numbering

Follow Semantic Versioning (SemVer):
- MAJOR.MINOR.PATCH (e.g., 1.2.3)
- MAJOR: Breaking changes
- MINOR: New features (backward compatible)
- PATCH: Bug fixes

### Creating a Release

1. **Update version**
   ```python
   # version.py
   __version__ = "1.2.0"
   ```

2. **Update CHANGELOG.md**
   ```markdown
   ## [1.2.0] - 2024-11-15
   ### Added
   - Voice interface support
   - Multi-language translations
   
   ### Fixed
   - Booking validation bug
   
   ### Changed
   - Improved recommendation algorithm
   ```

3. **Create git tag**
   ```bash
   git tag -a v1.2.0 -m "Release version 1.2.0"
   git push origin v1.2.0
   ```

4. **Create GitHub release**
   - Go to Releases
   - Create new release
   - Add release notes
   - Attach binaries if applicable

---

## Common Tasks

### Adding a New Cuisine Type

1. Edit `data/generator.py`:
   ```python
   CUISINES = [
       # ... existing
       "Ethiopian",  # Add new cuisine
   ]
   ```

2. Regenerate database:
   ```bash
   python data/generator.py
   ```

### Changing Response Time

1. Edit `agent/orchestrator.py`:
   ```python
   response = self.client.chat.completions.create(
       model=self.model_name,
       messages=messages,
       temperature=0.7,
       max_tokens=512,  # Reduce for faster responses
       top_p=0.9
   )
   ```

### Adding Analytics Metric

1. Edit `tools/analytics.py`:
   ```python
   def get_new_metric(self) -> Dict:
       with self.db.get_connection() as conn:
           cursor = conn.cursor()
           cursor.execute('''
               SELECT ... FROM ...
           ''')
           return cursor.fetchall()
   ```

2. Update `data/db_manager.py`:
   ```python
   def get_analytics(self) -> Dict:
       # ... existing code
       new_metric = self.get_new_metric()
       return {
           # ... existing metrics
           "new_metric": new_metric
       }
   ```

---

## Troubleshooting Development Issues

### Issue: Tests Failing Locally

**Solution**:
```bash
# Ensure clean environment
rm -rf venv
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# Regenerate database
python data/generator.py

# Run tests
python evaluation/test_scenarios.py
```

### Issue: Import Errors

**Solution**:
```bash
# Ensure you're in project root
cd restaurant-reservation-agent

# Activate virtual environment
source venv/bin/activate

# Verify Python path
python -c "import sys; print(sys.path)"
```

### Issue: Database Locked

**Solution**:
```python
# Use connection pooling
with self.db.get_connection() as conn:
    # Your code here
    pass  # Connection automatically closed
```

---

## Resources

### Learning Resources
- [Python Type Hints](https://docs.python.org/3/library/typing.html)
- [Streamlit Documentation](https://docs.streamlit.io)
- [SQLite Documentation](https://www.sqlite.org/docs.html)
- [Groq API Docs](https://console.groq.com/docs)

### Tools
- [Black](https://black.readthedocs.io/) - Code formatter
- [Flake8](https://flake8.pycqa.org/) - Style checker
- [MyPy](https://mypy.readthedocs.io/) - Type checker
- [Pytest](https://docs.pytest.org/) - Testing framework

---

## Questions?

- Check existing documentation
- Review closed issues/PRs
- Ask in discussions
- Contact maintainers

---

## Code of Conduct

### Our Standards
- Be respectful and inclusive
- Accept constructive criticism
- Focus on what's best for the project
- Show empathy towards others

### Unacceptable Behavior
- Harassment or discrimination
- Trolling or insulting comments
- Publishing private information
- Unprofessional conduct

---

## License

By contributing, you agree that your contributions will be licensed under the same license as the project (MIT License).

---

Thank you for contributing to the Restaurant Reservation AI Agent! 🎉
