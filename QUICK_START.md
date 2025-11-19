# 🚀 Quick Start Guide - Analysis Master

## Running the App

### Method 1: Double-Click Batch File (EASIEST)
```
Simply double-click: scripts\run_app_with_venv.bat
```
This automatically runs the app from your virtual environment!

### Method 2: Command Line
```bash
# Navigate to project
cd c:\Users\603506\Desktop\Trevor_Python\Stock_Platform

# Run from venv (CORRECT WAY)
venv\Scripts\streamlit run main.py

# DO NOT use global streamlit (WRONG)
# streamlit run main.py  ❌
```

### Method 3: PowerShell
```powershell
cd c:\Users\603506\Desktop\Trevor_Python\Stock_Platform
.\venv\Scripts\Activate.ps1
streamlit run main.py
```

---

### Method 4: Start full dev environment (Streamlit, Server, Worker)
```
# Use the helper batch script to open Streamlit, settings server, and worker in separate windows
scripts\start_dev_env.bat
```

### Method 5: Cross-platform start script
```bash
# On macOS/Linux you can use the helper shell script
scripts/start_dev_env.sh --with-redis --clean-cache
```

## Access the App

Once running, open your browser to:
- **Local:** http://localhost:8501
- **Network:** http://192.168.1.152:8501

---

## Common Issues & Solutions

### Issue: "ModuleNotFoundError: No module named 'X'"
**Cause:** Running streamlit from global Python instead of venv
**Solution:** Always use `venv\Scripts\streamlit` or run `scripts\run_app_with_venv.bat`

### Issue: "Port 8501 is already in use"
**Solution:**
```bash
# Find and kill the process
netstat -ano | findstr :8501
taskkill /F /PID <process_id>
```

### Issue: App won't start
**Solution:**
```bash
# Reinstall dependencies in venv
cd c:\Users\603506\Desktop\Trevor_Python\Stock_Platform
venv\Scripts\python.exe -m pip install -r requirements.txt --upgrade
```

---

## Development Workflow

### Starting a Development Session
1. Open terminal/PowerShell
2. Navigate to project: `cd c:\Users\603506\Desktop\Trevor_Python\Stock_Platform`
3. Run app: `venv\Scripts\streamlit run main.py`
4. Open browser to http://localhost:8501
5. Edit code - Streamlit auto-reloads!

Optionally: Use the helper `dev.bat` to run the app and related services. Pass `--skip-install` to avoid re-installing requirements for faster startup:

```bat
dev.bat start --skip-install
```

### Checking Current Progress
1. Open `PROJECT_PLAN.md` to see what's complete
2. Check `SESSION_HANDOFF.md` for the latest session notes
3. Review `PHASE_0_COMPLETE.md` for Phase 0 details

### Installing New Dependencies
```bash
# Always install to venv!
venv\Scripts\pip install <package_name>

# Then add to requirements.txt
echo <package_name>>=X.X.X >> requirements.txt
```

---

## File Locations

| What | Where |
|------|-------|
| Main app | `main.py` |
| Dashboards | `src/dashboards/` |
| Data pipelines | `src/pipelines/` |
| Analysis engines | `src/analysis/` |
| Core utilities | `src/core/` |
| API keys | `.streamlit/secrets.toml` (NEVER commit!) |
| Dependencies | `requirements.txt` |
| Project plan | `PROJECT_PLAN.md` |

---

## Next Development Tasks

See `SESSION_HANDOFF.md` for detailed next steps, but quick priorities:

1. **Build Equity Dashboard** (`src/dashboards/dashboard_equity.py`)
2. **Build Sentiment Scraper** (`src/pipelines/get_sentiment_scraper.py`)
3. **Build FMP Data Pipeline** (`src/pipelines/get_fmp_data.py`)
4. **Build Options Dashboard** (`src/dashboards/dashboard_options.py`)

---

## Key Commands

```bash
# Activate venv (if needed)
venv\Scripts\activate

# Run app
venv\Scripts\streamlit run main.py

# Install dependencies
venv\Scripts\pip install -r requirements.txt

# Check Python version
venv\Scripts\python --version

# Clear Streamlit cache (in Python)
from src.core.cache_manager import CacheManager
CacheManager.clear_all_cache()
```

### LLM worker & manual test commands
```bash
# Run worker in foreground (long-running)
venv\Scripts\python.exe scripts\run_llm_worker.py
# Run worker in once-mode (useful for CI/smoke tests)
venv\Scripts\python.exe scripts\run_llm_worker.py --once

```

---

## Quick Code Snippets

### Add a New Dashboard
```python
# In src/dashboards/dashboard_new.py
import streamlit as st

class NewDashboard:
    def __init__(self):
        self.name = "New Dashboard"

    def display(self):
        tab1, tab2, tab3 = st.tabs(["Summary", "Deep Dive", "AI Opinion"])

        with tab1:
            st.write("Summary content")

        with tab2:
            st.write("Deep dive content")

        with tab3:
            st.info("🤖 AI Opinion coming in Phase 5!")
```

### Fetch Stock Data
```python
from src.pipelines.get_market_data import get_stock_price, get_current_price

# Get historical data
df = get_stock_price("AAPL", period="1y")

# Get current price
price = get_current_price("AAPL")
```

### Display a Metric
```python
from src.core.design_system import MetricCardRenderer

MetricCardRenderer.render_metric(
    label="Stock Price",
    value="$175.32",
    delta="+2.45%",
    prefix="$"
)
```

---

## Getting Help

1. **Check Documentation:**
   - `README.md` - Full project overview
   - `PROJECT_PLAN.md` - Task tracker
   - `SESSION_HANDOFF.md` - Latest session notes
   - `PHASE_0_COMPLETE.md` - Phase 0 details

2. **Check Code Examples:**
   - `src/pipelines/get_market_data.py` - Data pipeline pattern
   - `src/core/design_system.py` - UI components
   - `src/dashboards/dashboard_selector.py` - Dashboard pattern

3. **Streamlit Docs:** https://docs.streamlit.io/

---

## Remember

- ✅ Always run from venv: `venv\Scripts\streamlit`
- ✅ Use `scripts\run_app_with_venv.bat` for easiest startup
- ✅ API keys in `.streamlit/secrets.toml` (never commit!)
- ✅ Update `PROJECT_PLAN.md` as you complete tasks
- ✅ Cache expensive operations with `@CacheManager` decorators

---

**Happy coding! 💎🙌🚀**
