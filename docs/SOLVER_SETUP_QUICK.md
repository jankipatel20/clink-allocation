# 🚀 Solver Setup - Quick Reference

## For You (No Conda, CBC Installed)

### Initial Setup
```bash
# 1. Copy template
cd backend
copy config.example.py config.py

# 2. Find your CBC path
where cbc.exe
# Example output: C:\Program Files\CBC\bin\cbc.exe

# 3. Update config.py
# Change line:
CBC_WINDOWS_PATH = r"C:\Program Files\CBC\bin\cbc.exe"

# 4. Test
python config.py
```

### Your config.py should have:
```python
PREFERRED_SOLVER = 'cbc'
CBC_WINDOWS_PATH = r"C:\Program Files\CBC\bin\cbc.exe"  # Your actual path
```

---

## For Your Teammate (With Conda)

### Initial Setup
```bash
# 1. Install CBC via conda
conda install -c conda-forge coincbc

# 2. Copy template
cd backend
cp config.example.py config.py

# 3. That's it! Auto-detection works
python config.py
```

### Their config.py needs NO changes!
Auto-detection handles everything.

---

## Git Workflow

### ✅ Safe to Commit
- `config.example.py` (template)
- `model.py` (uses config)
- `.gitignore` (excludes config.py)

### ❌ Never Committed
- `config.py` (your local settings)

### How It Works
```
You push:               Teammate pulls:
├─ model.py            ├─ model.py (updated)
├─ config.example.py   ├─ config.example.py (updated)
├─ .gitignore          ├─ .gitignore (updated)
└─ config.py (ignored) └─ config.py (their local, unchanged)

NO CONFLICTS! 🎉
```

---

## Quick Commands

### Test Configuration
```bash
python backend/config.py
```

### Test Backend
```bash
uvicorn backend.main:app --reload
```

### Test Optimization
```bash
# In browser or curl
curl -X POST http://localhost:8000/optimize
```

---

## Expected Output (CBC)

When optimization runs, you should see:
```
Welcome to the CBC MILP Solver
...
Optimal - objective value 4250000.50
```

---

## Troubleshooting

| Error | Solution |
|-------|----------|
| "cbc not found" | Update `CBC_WINDOWS_PATH` in config.py |
| "Cannot import config" | Run `copy config.example.py config.py` |
| "Permission denied" | Run terminal as administrator |
| CBC runs slow | Normal for first run, should be fast after |

---

## Solver Comparison

| Feature | CBC | GLPK |
|---------|-----|------|
| Speed | ⚡ Faster | Slower |
| MILP Support | ✅ Excellent | ✅ Good |
| Free | ✅ Yes | ✅ Yes |
| Conda Install | ✅ Easy | ✅ Easy |
| Recommended | ✅ **Default** | Backup |

---

## File Locations

```
backend/
├─ config.py              ← YOUR local settings (not in Git)
├─ config.example.py      ← Template (in Git)
└─ model.py               ← Updated to use CBC

.gitignore
└─ backend/config.py      ← Prevents Git conflicts
```

---

## Status: ✅ READY

- ✅ CBC solver configured
- ✅ Config system created
- ✅ Git conflicts prevented
- ✅ Auto-detection for conda
- ✅ Fallback to GLPK supported
- ✅ Documentation complete

**Next Step:** Test your optimization!
```bash
uvicorn backend.main:app --reload
```
