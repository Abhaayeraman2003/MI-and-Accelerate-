"""
Dashboard view for the DGW MI & Accelerate Streamlit app.

Gives an at-a-glance overview with graphs:
  * Top metric cards (initiatives, OpCos, avg Accelerate completion, RAG mix)
  * RAG status donut
  * Accelerate: overall completion gauge + per-initiative progress bars ("how far are they")
  * MI: maturity current-vs-target and progress
Works off submitted data OR the baseline deck data, filterable by OpCo.
"""

import statistics
import streamlit as st

import common

# optional Plotly (nicer gauges/donuts); fall back to native charts if missing
try:
    import plotly.graph_objects as go
    import plotly.express as px
    HAS_PLOTLY = True
except Exception:
    HAS_PLOTLY = False


def _gauge(pct, title):
    if HAS_PLOTLY:
        fig = go.Figure(go.Indicator(
            mode="gauge+number",
            value=round(pct, 1),
            number={"suffix": "%"},
            title={"text": title, "font": {"size": 14}},
            gauge={
                "axis": {"range": [0, 100]},
                "bar": {"color": "#0B0B0B"},
                "steps": [
                    {"range": [0, 40], "color": "#FDECEC"},
                    {"range": [40, 75], "color": "#FFF6E0"},
                    {"range": [75, 100], "color": "#E8F5E9"},
                ],
                "threshold": {"line": {"color": "#FFCB05", "width": 4}, "value": pct},
            },
        ))
        fig.update_layout(height=240, margin=dict(l=20, r=20, t=50, b=10))
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.metric(title, "%.1f%%" % pct)
        st.progress(min(1.0, pct / 100.0))


def _rag_donut(counts):
    labels = [k for k in ["Green", "Amber", "Red", "Blue", "Not set"] if counts.get(k)]
    values = [counts[k] for k in labels]
    if not values:
        st.info("No RAG data for the current selection.")
        return
    colors = [common.RAG_COLOR[k] for k in labels]
    if HAS_PLOTLY:
        fig = go.Figure(go.Pie(labels=labels, values=values, hole=0.55,
                               marker=dict(colors=colors), sort=False))
        fig.update_layout(height=300, margin=dict(l=10, r=10, t=10, b=10),
                          legend=dict(orientation="h"))
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.bar_chart({"count": {k: counts[k] for k in labels}})


def _progress_row(label, pct, right_text):
    c1, c2, c3 = st.columns([5, 3, 2])
    with c1:
        st.write(label)
    with c2:
        st.progress(min(1.0, pct / 100.0))
    with c3:
        st.write("**%.0f%%**  " % pct + (right_text or ""))


def render_dashboard(DATA):
    st.header("📊 MI & Accelerate — Executive Dashboard")

    # ---- data source ----
    src = st.radio("Data source", ["Submitted data", "Baseline (deck) data"],
                   horizontal=True,
                   help="‘Submitted data’ reads what OpCos have submitted through this app. "
                        "‘Baseline’ reads the current position on record from the deck.")

    records = []
    if src == "Submitted data":
        subs = common.load_submissions()
        records = common.submissions_to_records(subs)
        if not records:
            st.warning("No submissions found yet. Showing **baseline (deck) data** instead so you "
                       "can preview the dashboard.")
            src = "Baseline (deck) data"
    if src == "Baseline (deck) data" and not records:
        for country in DATA:
            records += common.iter_baseline_records(DATA, country)

    if not records:
        st.info("No data to display.")
        return

    # ---- filters ----
    all_opcos = sorted({r["opco"] for r in records})
    sel = st.multiselect("Filter OpCo(s)", all_opcos, default=all_opcos)
    records = [r for r in records if r["opco"] in sel]
    if not records:
        st.info("Nothing matches the current filter.")
        return

    accel = [r for r in records if r["kind"] == "Accelerate"]
    mi = [r for r in records if r["kind"] == "MI"]

    # ---- accelerate progress computation ----
    accel_prog = []
    for r in accel:
        pct, act, est, ek, ak = common.accel_progress(r["fields"])
        if pct is not None:
            accel_prog.append((r, pct, act, est))

    # ---- top metric cards ----
    rag_counts = {}
    for r in records:
        if r["kind"] in ("Accelerate", "MI"):
            b = common.rag_bucket(r["fields"].get("RAG Status", ""))
            rag_counts[b] = rag_counts.get(b, 0) + 1
    avg_accel = statistics.mean([p for _, p, _, _ in accel_prog]) if accel_prog else 0.0
    green = rag_counts.get("Green", 0)
    rated = sum(v for k, v in rag_counts.items() if k != "Not set")
    green_pct = (green / rated * 100.0) if rated else 0.0

    m1, m2, m3, m4 = st.columns(4)
    m1.metric("OpCos in view", len(sel))
    m2.metric("Initiatives", len(records))
    m3.metric("Avg Accelerate completion", "%.1f%%" % avg_accel)
    m4.metric("RAG green", "%.0f%%" % green_pct, help="Share of rated initiatives marked Green")

    st.divider()

    # ---- RAG + overall gauge ----
    c1, c2 = st.columns([1, 1])
    with c1:
        st.subheader("RAG status mix")
        _rag_donut(rag_counts)
    with c2:
        st.subheader("Overall Accelerate completion")
        _gauge(avg_accel, "Actual ÷ Estimated impact")
        st.caption("Averaged across %d Accelerate initiative(s) with reported figures." % len(accel_prog))

    st.divider()

    # ---- Accelerate: per-initiative progress ("how far are they") ----
    st.subheader("🚀 Accelerate — how far each initiative is")
    if not accel_prog:
        st.info("No Accelerate initiatives with both estimated and actual impact in this selection.")
    else:
        # bar chart of completion, sorted
        chart_rows = sorted(accel_prog, key=lambda x: x[1], reverse=True)
        if HAS_PLOTLY:
            labels = [("%s · %s" % (r["opco"], r["initiative"]))[:60] for r, _, _, _ in chart_rows]
            vals = [round(p, 1) for _, p, _, _ in chart_rows]
            colors = ["#2E7D32" if v >= 75 else "#E8A317" if v >= 40 else "#C62828" for v in vals]
            fig = go.Figure(go.Bar(x=vals, y=labels, orientation="h",
                                   marker=dict(color=colors),
                                   text=[f"{v}%" for v in vals], textposition="auto"))
            fig.update_layout(height=max(300, 26 * len(vals)),
                              margin=dict(l=10, r=10, t=10, b=10),
                              xaxis=dict(title="% of estimated impact achieved", range=[0, 100]),
                              yaxis=dict(autorange="reversed"))
            st.plotly_chart(fig, use_container_width=True)

        # grouped progress sliders per OpCo
        by_opco = {}
        for r, p, act, est in accel_prog:
            by_opco.setdefault(r["opco"], []).append((r, p, act, est))
        for opco in sorted(by_opco):
            with st.expander("%s — %d initiative(s)" % (opco, len(by_opco[opco])),
                             expanded=(len(by_opco) <= 2)):
                for r, p, act, est in sorted(by_opco[opco], key=lambda x: x[1], reverse=True):
                    right = "(%s / %s)" % (_fmt(act), _fmt(est))
                    _progress_row(r["initiative"], p, right)

    st.divider()

    # ---- MI maturity ----
    st.subheader("📈 MI — maturity toward target")
    mi_prog = []
    for r in mi:
        mp, cur, tgt = common.maturity_progress(r["fields"])
        if mp is not None:
            mi_prog.append((r, mp, cur, tgt))
    if not mi_prog:
        st.info("No MI initiatives with current & target maturity in this selection.")
    else:
        avg_mi = statistics.mean([p for _, p, _, _ in mi_prog])
        cA, cB = st.columns([1, 2])
        with cA:
            _gauge(avg_mi, "Avg maturity vs target")
        with cB:
            if HAS_PLOTLY:
                labels = [("%s · %s" % (r["opco"], r["initiative"]))[:55] for r, _, _, _ in
                          sorted(mi_prog, key=lambda x: x[1])]
                vals = [round(p, 0) for _, p, _, _ in sorted(mi_prog, key=lambda x: x[1])]
                fig = go.Figure(go.Bar(x=vals, y=labels, orientation="h",
                                       marker=dict(color="#1565C0"),
                                       text=[f"{int(v)}%" for v in vals], textposition="auto"))
                fig.update_layout(height=max(280, 24 * len(vals)),
                                  margin=dict(l=10, r=10, t=10, b=10),
                                  xaxis=dict(title="Current maturity as % of target", range=[0, 100]))
                st.plotly_chart(fig, use_container_width=True)
            else:
                for r, p, cur, tgt in sorted(mi_prog, key=lambda x: x[1], reverse=True):
                    _progress_row("%s · %s" % (r["opco"], r["initiative"]), p, "%s→%s" % (cur, tgt))

    st.caption("Note: Accelerate % = reported actual ÷ estimated impact; where OpCos report in "
               "different units the figure is indicative. Maturity % maps Basic→Intermediate→Control→Advanced.")


def _fmt(n):
    if n is None:
        return "—"
    a = abs(n)
    if a >= 1e9:
        return "%.2fBn" % (n / 1e9)
    if a >= 1e6:
        return "%.1fMn" % (n / 1e6)
    if a >= 1e3:
        return "%.0fk" % (n / 1e3)
    return "%.0f" % n
