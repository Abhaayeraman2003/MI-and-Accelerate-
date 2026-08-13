# DGW MI & Accelerate — Excel edition

Everything is stored in ONE master Excel workbook: **submissions.xlsx**.

## Run it
Windows: double-click `run_windows.bat`  ·  Mac/Linux: `./run_mac_linux.sh`
…or:  `pip install -r requirements.txt`  then  `streamlit run streamlit_app.py`

## How it works
- **📝 Submit** → the OpCo's answers are written into `submissions.xlsx`
  (sheet **“Submissions”** = a clean, filterable table; one row per initiative with OpCo,
  RAG, Accelerate %, Actual, Estimated, Maturity, Comment). Re-submitting the same OpCo +
  month overwrites its rows (no duplicates). Each person also gets an Excel copy to download.
- **📊 Dashboard** → reads `submissions.xlsx` and shows the tracker, charts, RAG mix and
  Accelerate progress, with a **“Download master Excel”** button.

You can also just open `submissions.xlsx` directly in Excel — the “Submissions” sheet is
ready to filter, pivot, or chart.

## ⚠️ IMPORTANT about Streamlit Cloud
Streamlit Cloud storage is **temporary** — `submissions.xlsx` is wiped when the app
restarts, and different viewers can hit different servers. So on Streamlit Cloud this is
great for a **demo**, but for real collection from 20 people either:
  * run it **locally** (the file persists on your PC), OR
  * host the master workbook on **OneDrive/SharePoint** (ask me — only `excel_store.py` changes).

## Files
`streamlit_app.py` · `dashboard.py` · `excel_store.py` (the Excel storage) ·
`common.py` · `excel_builder.py` · `data.json` (replace with your full 14-OpCo file).
