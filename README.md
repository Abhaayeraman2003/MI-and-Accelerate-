# MTN EBU — MI & Accelerate Monthly Update (Streamlit)

A web form where each OpCo updates their MI & Accelerate initiatives. On submit, the rows
are appended (via Power Automate) to ONE master Excel file in your OneDrive
(**MI and Accelerate / submissions.xlsx**). Submitters can't access the master file.

## What's in this repo
| File | Purpose |
|------|---------|
| `streamlit_app.py` | The app (Submit form + admin Dashboard) |
| `dashboard.py` | Admin dashboard (passcode-protected) |
| `excel_store.py` | Sends each submission to your Power Automate flow → OneDrive |
| `excel_builder.py` | Builds each submitter's own Excel copy |
| `common.py` | Shared helpers / calculations |
| `data.json` | All 14 OpCos and their initiatives |
| `requirements.txt` | Dependencies |
| `.streamlit/config.toml` | MTN theme |
| `.streamlit/secrets.toml.example` | Template for `flow_url` + `admin_pin` |
| `master_submissions_TEMPLATE.xlsx` | The pre-made master file to upload to OneDrive (NOT needed in the repo, but handy) |

## Deploy on Streamlit Cloud
1. Push this whole folder to a GitHub repo.
2. **share.streamlit.io** → **New app** → pick the repo → **Main file:** `streamlit_app.py` → **Deploy**.
3. In the app → **Settings → Secrets**, paste:
   ```toml
   flow_url = "https://prod-....logic.azure.com/...invoke?..."
   admin_pin = "your-passcode"
   ```
4. Reboot the app.

## OneDrive master file (Power Automate)
- Upload `master_submissions_TEMPLATE.xlsx` to your OneDrive **MI and Accelerate** folder
  and rename it **submissions.xlsx** (it already has the `Submissions` table).
- Build a Power Automate *“When an HTTP request is received”* flow that loops the incoming
  `rows` and does **Excel → “Add a row into a table”** into that file's `Submissions` table.
- Put the flow's HTTP URL into `flow_url` (above).

Full click-by-click steps are in **SETUP_OneDrive_OneFile.md** (delivered alongside this).

## Notes
- **No secrets set?** The app falls back to a local `submissions.xlsx` next to the code —
  good for testing on your PC (`pip install -r requirements.txt` then
  `streamlit run streamlit_app.py`).
- The Dashboard (admin) is passcode-protected; submitters only get their own Excel copy.
- Every row is date & time-stamped (Submitted date / Submitted time columns, UTC).
