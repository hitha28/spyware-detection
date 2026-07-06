# Architecture Notes

## Known Setup Issues

- **yara-python**: commented out in requirements.txt. It has no pre-built
  wheel for Python 3.14 on Windows and needs Microsoft C++ Build Tools to
  compile from source. Options before Phase 1 starts:
    1. Install Microsoft C++ Build Tools and uncomment the line, or
    2. Use Python 3.11/3.12 in a separate venv for the parts of the project
       needing yara-python.
  Flagging for Shivanshi ahead of P1-SHI3 (YARA rule set).
