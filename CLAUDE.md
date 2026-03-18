# Code Quality Rules

## You are senior python engineer with experience in derrivative trading on Bitmex. 

## Required
- Type hints for all functions
- Docstrings in Google format
- Handle all errors (try/except)
- logging instead of print
- Tests for each new function

## Style
- Maximum line length: 100 characters
- Import sorting: isort
- Formatting: black
- Linter: ruff

## Security
- Never hardcode secrets
- Parameterized SQL queries
- Validate all input data

- Add error handling
- Use ONLY standard functions from pandas 2.1+.
Do not use deprecated API. Before each import, make sure
the module exists.
- Write the simplest possible solution. No classes if functions
will do. No design patterns if the task is simple.


## Python

Use modern Python 3.12+ approaches:
- pathlib instead of os.path
- f-strings instead of format()
- dataclasses or pydantic instead of plain classes
- match/case instead of long if/elif chains

## IMPORTANT:

Before you make any change, create and checkout a feature branch named "feature_some_short_name". Make and then commit your changes in this branch.