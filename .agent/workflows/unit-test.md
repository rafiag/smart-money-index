---
description: Generate unit tests for Python files using pytest
---

1. **Analyze Context**: Identify all Python files currently in the active context or recently modified.
2. **Generate Tests**: For each identified Python file (e.g., `path/to/module.py`):
    - Create a corresponding test file (e.g., `tests/test_module.py` or alongside the file if preferred by project structure).
    - Use the `pytest` framework.
    - For every function and class method, implement:
        - At least one **positive test case** (typical expected input).
        - At least one **edge case** (e.g., empty input, extreme values, or error conditions).
3. **Verify**: Run the newly generated tests using `pytest` to ensure they pass or correctly identify issues.
4. **Report**: Summarize the created test files and the coverage achieved.
