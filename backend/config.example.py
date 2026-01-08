"""
Solver Configuration Template

INSTRUCTIONS:
1. Copy this file to 'config.py' in the same directory
2. Update the paths below according to your local setup
3. The config.py file is in .gitignore, so your changes won't cause merge conflicts

SETUP OPTIONS:
- Option A: You have conda installed → CBC/GLPK will auto-detect from conda env
- Option B: You have CBC installed manually → Update CBC_WINDOWS_PATH below
- Option C: You have GLPK installed manually → Update GLPK_WINDOWS_PATH below
"""

import os
import platform

# ============================================
# SOLVER CONFIGURATION
# ============================================

# Preferred solver: 'cbc' or 'glpk'
PREFERRED_SOLVER = 'cbc'

# ============================================
# CBC SOLVER PATHS
# ============================================

# For Windows without conda (coin-or CBC installed manually)
# Common installation paths:
# - C:\Program Files\CBC\bin\cbc.exe
# - C:\Program Files (x86)\CBC\bin\cbc.exe
# - C:\coin-or\CBC\bin\cbc.exe
CBC_WINDOWS_PATH = r"C:\Program Files\CBC\bin\cbc.exe"

# For conda environment (CBC installed via conda)
CBC_CONDA_PATH = None  # Will auto-detect from conda environment

# For Linux/Mac
CBC_UNIX_PATH = "cbc"  # Usually in system PATH

# ============================================
# GLPK SOLVER PATHS (Backup)
# ============================================

# For Windows GLPK
# Update this path if you have GLPK installed elsewhere
GLPK_WINDOWS_PATH = r"C:\Users\ADMIN\Downloads\winglpk-4.65\glpk-4.65\w64\glpsol.exe"

# For conda environment (GLPK installed via conda)
GLPK_CONDA_PATH = None  # Will auto-detect from conda environment

# For Linux/Mac
GLPK_UNIX_PATH = "glpsol"  # Usually in system PATH

# ============================================
# SOLVER OPTIONS
# ============================================

# CBC solver options
CBC_OPTIONS = {
    'tee': True,  # Show solver output
    'keepfiles': False,  # Don't keep temporary files
    'warmstart': False,
}

# GLPK solver options
GLPK_OPTIONS = {
    'tee': True,  # Show solver output
}

# Timeout in seconds (0 = no timeout)
SOLVER_TIMEOUT = 300  # 5 minutes

# ============================================
# AUTO-DETECTION FUNCTIONS
# ============================================

def get_solver_path(solver_name='cbc'):
    """
    Auto-detect solver path based on operating system and environment.
    
    Args:
        solver_name: 'cbc' or 'glpk'
    
    Returns:
        tuple: (solver_name, solver_path or None)
    """
    system = platform.system()
    
    if solver_name.lower() == 'cbc':
        # Check if running in conda environment
        if 'CONDA_PREFIX' in os.environ:
            # Running in conda - CBC should be in PATH
            return 'cbc', None  # None means use PATH
        
        # Not in conda - use manual installation path
        if system == 'Windows':
            if os.path.exists(CBC_WINDOWS_PATH):
                return 'cbc', CBC_WINDOWS_PATH
            else:
                # Try to find cbc.exe in common locations
                common_paths = [
                    r"C:\Program Files\CBC\bin\cbc.exe",
                    r"C:\Program Files (x86)\CBC\bin\cbc.exe",
                    r"C:\coin-or\CBC\bin\cbc.exe",
                ]
                for path in common_paths:
                    if os.path.exists(path):
                        return 'cbc', path
                # If not found, return None to try PATH
                return 'cbc', None
        else:
            # Linux/Mac - use system PATH
            return 'cbc', CBC_UNIX_PATH
    
    elif solver_name.lower() == 'glpk':
        # Check if running in conda environment
        if 'CONDA_PREFIX' in os.environ:
            return 'glpk', None  # Use PATH
        
        # Not in conda - use manual installation path
        if system == 'Windows':
            if os.path.exists(GLPK_WINDOWS_PATH):
                return 'glpk', GLPK_WINDOWS_PATH
            else:
                return 'glpk', None
        else:
            return 'glpk', GLPK_UNIX_PATH
    
    else:
        raise ValueError(f"Unknown solver: {solver_name}")


def get_solver_options(solver_name='cbc'):
    """
    Get solver-specific options.
    
    Args:
        solver_name: 'cbc' or 'glpk'
    
    Returns:
        dict: Solver options
    """
    if solver_name.lower() == 'cbc':
        return CBC_OPTIONS.copy()
    elif solver_name.lower() == 'glpk':
        return GLPK_OPTIONS.copy()
    else:
        return {'tee': True}


# ============================================
# CONFIGURATION SUMMARY
# ============================================

if __name__ == "__main__":
    print("=" * 60)
    print("SOLVER CONFIGURATION")
    print("=" * 60)
    print(f"Operating System: {platform.system()}")
    print(f"Preferred Solver: {PREFERRED_SOLVER}")
    print(f"Conda Environment: {'Yes' if 'CONDA_PREFIX' in os.environ else 'No'}")
    print()
    
    solver, path = get_solver_path(PREFERRED_SOLVER)
    print(f"Solver: {solver}")
    print(f"Path: {path if path else 'Using system PATH'}")
    print(f"Options: {get_solver_options(solver)}")
    print("=" * 60)
