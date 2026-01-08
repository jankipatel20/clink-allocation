# Solver Configuration Guide

## Overview

This project uses **CBC (Coin-or Branch and Cut)** solver by default, with GLPK as a fallback option. The configuration system supports multiple developer setups without causing Git merge conflicts.

## Quick Setup

### Step 1: Copy Configuration Template

```bash
cd backend
cp config.example.py config.py
```

### Step 2: Choose Your Setup

#### Option A: You Have Conda (Recommended for teammates)

If you have conda installed and CBC in your conda environment:

```bash
# Install CBC via conda
conda install -c conda-forge coincbc

# No need to modify config.py - it will auto-detect!
```

**In `config.py`**: No changes needed! Auto-detection will work.

#### Option B: You Have CBC Installed Manually (Current setup)

If you have coin-or CBC installed outside conda:

1. Find your CBC installation path (e.g., `C:\Program Files\CBC\bin\cbc.exe`)
2. Update `config.py`:

```python
CBC_WINDOWS_PATH = r"C:\Program Files\CBC\bin\cbc.exe"  # Your path here
PREFERRED_SOLVER = 'cbc'
```

#### Option C: You Want to Use GLPK Instead

If you prefer GLPK:

1. Update `config.py`:

```python
PREFERRED_SOLVER = 'glpk'
GLPK_WINDOWS_PATH = r"C:\path\to\glpsol.exe"  # Your GLPK path
```

### Step 3: Verify Configuration

Run the configuration checker:

```bash
python backend/config.py
```

You should see output like:

```
============================================================
SOLVER CONFIGURATION
============================================================
Operating System: Windows
Preferred Solver: cbc
Conda Environment: No

Solver: cbc
Path: C:\Program Files\CBC\bin\cbc.exe
Options: {'tee': True, 'keepfiles': False, 'warmstart': False}
============================================================
```

## How It Works

### For You (No Conda, CBC Installed)

- `config.py` is in `.gitignore` - your local settings won't be committed
- Your `CBC_WINDOWS_PATH` points to your local CBC installation
- When you run optimization, it uses your CBC path

### For Your Teammate (With Conda)

- They copy `config.example.py` to `config.py`
- They install CBC via conda: `conda install -c conda-forge coincbc`
- Their `config.py` auto-detects CBC from conda environment
- No path configuration needed!

### No Merge Conflicts

```
You:                          Teammate:
config.py (local)            config.py (local)
├─ CBC_WINDOWS_PATH          ├─ CBC_WINDOWS_PATH (unused)
│  = C:\...\cbc.exe          │  = default value
├─ Uses manual path          ├─ Auto-detects conda
└─ NOT in Git                └─ NOT in Git

Both work independently!
config.example.py is tracked in Git (reference only)
```

## Testing Your Setup

### Test 1: Check Configuration

```bash
python backend/config.py
```

**Expected Output:**
- Shows your solver name (cbc or glpk)
- Shows the path being used
- No errors

### Test 2: Run Optimization

```bash
# Start backend
uvicorn backend.main:app --reload

# In another terminal
curl -X POST http://localhost:8000/optimize
```

**Expected:**
- Solver runs successfully
- No "solver not found" errors

### Test 3: Check Solver Output

Look for CBC-specific output in the logs:

```
Welcome to the CBC MILP Solver
...
Optimal - objective value 4250000.50
```

## Troubleshooting

### Error: "Solver 'cbc' not found"

**Solution 1:** Verify CBC installation

```bash
# Windows
where cbc
# Should show path to cbc.exe

# Linux/Mac
which cbc
```

**Solution 2:** Update path in `config.py`

```python
CBC_WINDOWS_PATH = r"C:\correct\path\to\cbc.exe"
```

**Solution 3:** Use GLPK as fallback

```python
PREFERRED_SOLVER = 'glpk'
```

### Error: "Cannot import config"

**Solution:** Create `config.py` from template

```bash
cd backend
cp config.example.py config.py
```

### CBC runs but solver fails

**Check CBC version:**

```bash
cbc.exe -v
```

**Recommended:** CBC 2.10.5 or later

**If using conda:**

```bash
conda update -c conda-forge coincbc
```

## Installing CBC

### For Windows (Manual Installation)

1. Download CBC from: https://github.com/coin-or/Cbc/releases
2. Extract to `C:\Program Files\CBC`
3. Update `config.py` with the path to `cbc.exe`

### For Windows (Conda)

```bash
conda install -c conda-forge coincbc
```

### For Linux

```bash
sudo apt-get install coinor-cbc
```

### For macOS

```bash
brew install cbc
```

## Switching Solvers

To switch from CBC to GLPK (or vice versa):

1. Update `config.py`:

```python
PREFERRED_SOLVER = 'glpk'  # or 'cbc'
```

2. Restart the backend

3. Run optimization

The model will automatically use the new solver!

## Advanced Configuration

### Custom Solver Options

Edit `config.py`:

```python
CBC_OPTIONS = {
    'tee': True,          # Show solver output
    'keepfiles': False,   # Don't keep temporary files
    'warmstart': False,   # Don't use warm start
    'ratio': 0.1,         # MIP gap tolerance (10%)
}
```

### Timeout Settings

```python
SOLVER_TIMEOUT = 600  # 10 minutes
```

### Multiple Solver Paths

```python
# Try multiple locations
def get_solver_path(solver_name='cbc'):
    if solver_name == 'cbc':
        paths_to_try = [
            r"C:\Program Files\CBC\bin\cbc.exe",
            r"C:\coin-or\bin\cbc.exe",
            r"D:\Solvers\CBC\cbc.exe",
        ]
        for path in paths_to_try:
            if os.path.exists(path):
                return 'cbc', path
    # ... rest of function
```

## Git Workflow

### When You Make Changes

```bash
# Your config.py is ignored - won't be committed
git status
# Should NOT show config.py

git add .
git commit -m "Updated model"
git push
```

### When Your Teammate Pulls

```bash
git pull
# Their config.py is NOT affected
# They keep their local settings
```

### Sharing Config Changes

If you need to update the template:

```bash
# Update config.example.py (tracked in Git)
vim backend/config.example.py

git add backend/config.example.py
git commit -m "Updated config template"
git push

# Teammates can merge and update their config.py if needed
```

## File Structure

```
backend/
├─ config.py              ← Your local config (in .gitignore)
├─ config.example.py      ← Template (tracked in Git)
├─ model.py               ← Uses config.py
└─ main.py                ← Uses model.py

.gitignore
└─ backend/config.py      ← Prevents config.py from being committed
```

## Summary

✅ **CBC solver** is now the default
✅ **config.py** manages solver paths
✅ **Auto-detection** works for conda environments
✅ **No merge conflicts** - each developer has their own config.py
✅ **Backward compatible** - falls back to GLPK if needed
✅ **Template available** - config.example.py for teammates

Your setup:
- You: No conda, CBC at `C:\Program Files\CBC\bin\cbc.exe`
- Teammate: Conda, CBC auto-detected from environment

Both work perfectly without conflicts! 🎉
