# One master Excel on your OneDrive — setup (≈10 min, no IT needed)

Result: a single file **submissions.xlsx** in your OneDrive **MI and Accelerate** folder that
updates itself every time someone submits. Only you can open it.

## Step 1 — Put the master file in OneDrive
1. OneDrive → open your **MI and Accelerate** folder.
2. Upload **master_submissions_TEMPLATE.xlsx** (from this repo) and rename it **submissions.xlsx**.
   (It already contains the `Submissions` table the flow writes into. Keep the header row;
   you can delete the “(sample)” row once real data arrives.)

## Step 2 — Build the flow (Power Automate)
1. make.powerautomate.com → **Create → Instant cloud flow** → trigger
   **“When an HTTP request is received”**.
2. In the trigger → **Use sample payload to generate schema**, paste:
   ```json
   { "opco":"Ghana","reportingMonth":"August 2026","submittedBy":"Deniel",
     "rows":[ {"OpCo":"Ghana","Reporting month":"August 2026","Submitted by":"Deniel",
       "Email":"d@mtn.com","Type":"Accelerate Initiatives","Section":"","Initiative":"1.2 Reseller",
       "RAG":"Amber","Accelerate %":25,"Actual":"538992","Estimated":"2151994","Maturity %":"",
       "Current":"","Target":"","Comment":"","Submitted UTC":"2026-08-14T13:00:00Z",
       "Submitted date":"2026-08-14","Submitted time":"13:00:00"} ] }
   ```
3. **+ New step → Apply to each** → output = **rows**.
4. Inside → **Excel Online (Business) → Add a row into a table**:
   - Location: OneDrive for Business · Library: OneDrive
   - File: `MI and Accelerate/submissions.xlsx` · Table: `Submissions`
   - Map each column box to the matching dynamic item property.
5. **Save** → open the trigger → copy the **HTTP POST URL**.

## Step 3 — Tell the app
Streamlit Cloud → your app → **Settings → Secrets**:
```toml
flow_url  = "PASTE-THE-HTTP-POST-URL"
admin_pin = "your-passcode"
```
Reboot the app. Done — every submit now appends to submissions.xlsx in your OneDrive.

## View it
OneDrive → MI and Accelerate → submissions.xlsx. Filter the **OpCo** column (or Insert →
PivotTable) for a per-OpCo view. Date/time stamps are in the Submitted date/time columns.
