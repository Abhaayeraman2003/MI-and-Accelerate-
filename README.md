# DGW MI & Accelerate — Monthly OpCo Update + Dashboard (Streamlit)

A **Streamlit** app for the MTN EBU monthly MI & Accelerate process, with two views
(switch in the sidebar):

- **📝 Submit update** — each OpCo picks their country + month, edits only what changed
  (everything is pre-filled from the deck), and submits. The app builds a styled **Excel
  workbook** and files it automatically under
  `MI and Accelerate / <Country> / <Year> / <Month> / MI_Accelerate_<Country>_<YYYYMM>.xlsx`.
- **📊 Dashboard** — an executive overview with graphs:
  - Top metric cards (OpCos, initiatives, avg Accelerate completion, RAG green %)
  - **RAG status donut**
  - **Overall Accelerate completion gauge** + a **progress bar for every initiative**
    ("how far are they" = actual ÷ estimated impact)
  - **MI maturity** gauge + current-vs-target bars
  - Filter by one or many OpCos; read from **submitted data** or **baseline deck data**

---

## Files

| File | Purpose |
|------|---------|
| `streamlit_app.py` | Entry point — sidebar view switch, submit form |
| `dashboard.py` | The dashboard view (graphs, gauges, progress bars) |
| `common.py` | Shared constants, helpers, number/RAG/maturity parsing, storage & submission loading |
| `excel_builder.py` | Server-side styled Excel builder (RAG colours, one sheet per section) |
| `data.json` | All 14 OpCos and their initiatives (extracted from the deck form) |
| `requirements.txt` | Dependencies (Streamlit, openpyxl, plotly, google-cloud-storage) |
| `.streamlit/config.toml` | MTN yellow/black theme |
| `.streamlit/secrets.toml.example` | Template for Google Cloud Storage credentials |

---

## 1. Run locally

```bash
cd dgw-mi-accelerate-streamlit
python -m venv .venv
# Windows:  .venv\Scripts\activate     |  macOS/Linux:  source .venv/bin/activate
pip install -r requirements.txt
streamlit run streamlit_app.py
```

Opens at **http://localhost:8501**. With no secrets set, submissions save to a local
`submissions/` folder. The dashboard reads those submissions (or, if none yet, previews
the baseline deck data so it's never empty).

---

## 2. Push to GitHub

```bash
cd dgw-mi-accelerate-streamlit
git init && git add . && git commit -m "MI & Accelerate Streamlit app + dashboard"
git branch -M main
git remote add origin https://github.com/<your-username>/dgw-mi-accelerate-streamlit.git
git push -u origin main
```

---

## 3. Host free on Streamlit Community Cloud

1. **share.streamlit.io** → sign in with GitHub → **New app**.
2. Pick your repo, branch `main`, main file `streamlit_app.py` → **Deploy**.
3. You get a public URL like `https://dgw-grad-base.streamlit.app` to share with OpCos.

> Streamlit Cloud's disk is temporary — for submissions that **persist**, add Google Cloud
> Storage (step 4).

---

## 4. Persistent storage — Google Cloud Storage (recommended when hosted)

1. In Google Cloud: create a bucket + a **service account** with *Storage Object Admin* on
   that bucket; download its **JSON key**.
2. Streamlit Cloud → your app → **Settings → Secrets**, paste (see `secrets.toml.example`):
   ```toml
   gcs_bucket = "your-bucket-name"
   [gcp_service_account]
   type = "service_account"
   project_id = "..."
   private_key = "-----BEGIN PRIVATE KEY-----\n...\n-----END PRIVATE KEY-----\n"
   client_email = "svc-...@your-project.iam.gserviceaccount.com"
   # ...rest of the JSON key fields
   ```
3. Save. Submissions now write to `gs://<bucket>/MI and Accelerate/<Country>/<Year>/<Month>/`,
   and the dashboard reads straight from the bucket.

---

## How the dashboard numbers work

- **Accelerate completion %** = reported **actual/YTD impact ÷ estimated impact** per
  initiative (0–100%). Handles messy figures like `2,151,994.21`, `1.7 Bn`, `575 Mn`, `20.96 m`.
  Where OpCos report in different units the figure is indicative.
- **MI maturity %** maps Basic→Intermediate→Control→Advanced and shows current as a % of target.
- **RAG** is normalised to Green / Amber / Red / Blue / Not set for the donut and metrics.

---

## Notes

- **Always downloadable:** after submitting, the OpCo can download their Excel copy.
- **Accents handled:** filenames use an ASCII-safe country slug (Côte d'Ivoire →
  `CotedIvoire`); the **folder** keeps the correct display spelling.
- **Plotly optional:** if Plotly isn't installed, the dashboard falls back to native
  Streamlit charts and progress bars automatically.
- **Want SharePoint instead of GCS?** Swap `save_bytes()` / `load_submissions()` in
  `common.py` for Microsoft Graph calls — the rest of the app is unchanged.
