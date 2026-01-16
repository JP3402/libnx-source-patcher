# Libnx Source Patcher

This tool is designed for Nintendo Switch homebrew developers. It automates the process of updating the `libnx` source code within a project to the latest version.

## IMPORTANT

This tool works on **source code projects**, not compiled `.nro` or `.ovl` files. Due to the complexities of compiled binaries, it is not feasible to patch them directly. The only reliable way to update the `libnx` version of an application is to recompile it from source with the updated library.

## Installation

Before running the script, install the required dependency:

```bash
pip install -r requirements.txt

## Usage

Run the script and provide the path to your homebrew project directory:

```
python3 source/main.py /path/to/your/project
```

The script will:
1. Fetch the latest `libnx` source code from the official repository.
2. Find the `libnx` (or `nx`) directory within your project.
3. **Ask for your confirmation** before replacing the old files with the new ones. (You can bypass this with the `-y` flag).
4. Provide instructions for compiling your project.
