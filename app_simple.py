import streamlit as st
import pandas as pd
st.warning("Educational simulation only. Not official financial reporting. Use for learning and discussion.")
st.caption("v0.1 (testing)")

st.set_page_config(page_title="Plant Margin Simulator", layout="wide")

# ======================================================
# Fixed Baseline (edit once here)
# ======================================================
BASELINE = {
    "price_per_ton": 500.0,
    "run_rate_tph": 120.0,
    "planned_hours_per_month": 600.0,
    "downtime_hours": 40.0,
    "yield_pct": 95.0,
    "energy_cost_per_ton": 35.0,
    "labor_cost_per_ton": 25.0,
    "scrap_pct": 1.0,
    "other_variable_cost_per_ton": 60.0,
    "fixed_cost_per_month": 2_000_000.0,
}

# ======================================================
# Helpers
# ======================================================
def clamp(x, lo=0.0, hi=1.0):
    return max(lo, min(hi, x))

def money0(x):
    return f"${x:,.0f}"

def money2(x):
    return f"${x:,.2f}"

def arrow(delta, tol=1e-9):
    if delta > tol:
        return "▲"
    if delta < -tol:
        return "▼"
    return "●"

def delta_class(delta, tol=1e-9):
    if delta > tol:
        return "pos"
    if delta < -tol:
        return "neg"
    return "neu"

def value_class(val):
    # EBITDA value: black if positive, red if negative
    return "neutral" if val > 0 else "neg"

def colorize(text, delta):
    return f"<span class='{delta_class(delta)}'>{text}</span>"

# ======================================================
# Core Financial Engine (names match BASELINE keys)
# ======================================================
def compute_metrics(
    price_per_ton: float,
    run_rate_tph: float,
    planned_hours_per_month: float,
    downtime_hours: float,
    yield_pct: float,
    energy_cost_per_ton: float,
    labor_cost_per_ton: float,
    scrap_pct: float,
    other_variable_cost_per_ton: float,
    fixed_cost_per_month: float,
):
    downtime_hours = max(0.0, min(downtime_hours, planned_hours_per_month))
    operating_hours = planned_hours_per_month - downtime_hours
    tons_processed = run_rate_tph * operating_hours

    yield_frac = clamp(yield_pct / 100.0, 0.50, 1.00)
    scrap_frac = clamp(scrap_pct / 100.0, 0.0, 0.20)

    saleable_tons = tons_processed * yield_frac
    net_saleable_tons = saleable_tons * (1.0 - scrap_frac)

    revenue = net_saleable_tons * price_per_ton
    variable_cost = tons_processed * (
        energy_cost_per_ton + labor_cost_per_ton + other_variable_cost_per_ton
    )

    contribution = revenue - variable_cost
    ebitda = contribution - fixed_cost_per_month

    return {
        "Operating hours": operating_hours,
        "Tons processed": tons_processed,
        "Net saleable tons": net_saleable_tons,
        "Revenue": revenue,
        "Variable cost": variable_cost,
        "Contribution": contribution,
        "Contribution %": (contribution / revenue) * 100 if revenue else 0,
        "Fixed cost": fixed_cost_per_month,
        "EBITDA": ebitda,
        "EBITDA %": (ebitda / revenue) * 100 if revenue else 0,
        "Var cost / processed ton": (variable_cost / tons_processed) if tons_processed else 0,
        "Contribution / processed ton": (contribution / tons_processed) if tons_processed else 0,
    }

# ======================================================
# Session State Defaults (Reset)
# ======================================================
DEFAULTS = {
    "price_per_ton": int(BASELINE["price_per_ton"]),
    "run_rate_tph": int(BASELINE["run_rate_tph"]),
    "planned_hours_per_month": int(BASELINE["planned_hours_per_month"]),
    "downtime_hours": int(BASELINE["downtime_hours"]),
    "yield_pct": float(BASELINE["yield_pct"]),
    "scrap_pct": float(BASELINE["scrap_pct"]),
    "energy_cost_per_ton": int(BASELINE["energy_cost_per_ton"]),
    "labor_cost_per_ton": int(BASELINE["labor_cost_per_ton"]),
    "other_variable_cost_per_ton": int(BASELINE["other_variable_cost_per_ton"]),
    "fixed_cost_per_month": int(BASELINE["fixed_cost_per_month"]),
}

for k, v in DEFAULTS.items():
    if k not in st.session_state:
        st.session_state[k] = v

def reset_to_baseline():
    for k, v in DEFAULTS.items():
        st.session_state[k] = v
    st.rerun()

# ======================================================
# Page Title
# ======================================================
st.title("Educational simulation - Plant Margin Simulator - V1.0")
st.caption("Baseline is fixed. Adjust current scenario and compare results.")

# ======================================================
# Sidebar (Reset button on top)
# ======================================================
with st.sidebar:
    if st.button("🔄 Reset to Baseline", use_container_width=True):
        reset_to_baseline()

    st.markdown("---")
    st.header("🎮 Adjust Current Scenario")

    st.subheader("📈 Market & Throughput")
    price_per_ton = st.slider("💲 Selling price ($/ton)-USD 500", 200, 1200, key="price_per_ton", step=5)
    run_rate_tph = st.slider("🏭 Run rate (tons/hour)-120 tons", 20, 400, key="run_rate_tph", step=5)

    st.subheader("⏱ Time")
    planned_hours_per_month = st.slider("🗓 Planned hours/month-600 hrs", 200, 744, key="planned_hours_per_month", step=10)
    downtime_hours = st.slider("🛑 Downtime hours-40 hrs", 0, planned_hours_per_month, key="downtime_hours", step=1)

    st.subheader("🧪 Yield & Quality")
    yield_pct = st.slider("🎯 Yield (%)-95%", 80.0, 99.5, key="yield_pct", step=0.1)
    scrap_pct = st.slider("🧯 Scrap (%)-1%", 0.0, 10.0, key="scrap_pct", step=0.1)

    st.subheader("💸 Costs")
    energy_cost_per_ton = st.slider("⚡ Energy ($/ton)-USD 35", 0, 200, key="energy_cost_per_ton", step=1)
    labor_cost_per_ton = st.slider("👷 Labor ($/ton)-USD 25", 0, 200, key="labor_cost_per_ton", step=1)
    other_variable_cost_per_ton = st.slider("🧰 Other variable ($/ton)-USD 60", 0, 400, key="other_variable_cost_per_ton", step=1)
    fixed_cost_per_month = st.slider("🏢 Fixed cost ($/month)-USD 20,000,000", 0, 20_000_000, key="fixed_cost_per_month", step=50_000)

# ======================================================
# Compute baseline and current
# ======================================================
baseline = compute_metrics(**BASELINE)

current_inputs = {
    "price_per_ton": float(price_per_ton),
    "run_rate_tph": float(run_rate_tph),
    "planned_hours_per_month": float(planned_hours_per_month),
    "downtime_hours": float(downtime_hours),
    "yield_pct": float(yield_pct),
    "energy_cost_per_ton": float(energy_cost_per_ton),
    "labor_cost_per_ton": float(labor_cost_per_ton),
    "scrap_pct": float(scrap_pct),
    "other_variable_cost_per_ton": float(other_variable_cost_per_ton),
    "fixed_cost_per_month": float(fixed_cost_per_month),
}
current = compute_metrics(**current_inputs)

delta_ebitda = current["EBITDA"] - baseline["EBITDA"]

# ======================================================
# CSS
# ======================================================
st.markdown("""
<style>
.pos { color: #22c55e; font-weight: 800; }
.neg { color: #ef4444; font-weight: 800; }
.neutral { color: #000000; font-weight: 900; }
.neu { color: #9ca3af; font-weight: 700; }

.kpi-card { padding: 6px 0px; }
.kpi-label { font-size: 14px; color: #9ca3af; margin-bottom: 4px; }
.kpi-value { font-size: 2rem; font-weight: 600; }

.big-table table {
  width: 100% !important;
  font-size: 18px;
  table-layout: fixed;
  border-collapse: collapse;
}
.big-table thead th {
  background: #374151;
  color: white;
  font-weight: 900;
  padding: 12px;
  text-align: left;
}
.big-table td {
  padding: 10px;
  border-bottom: 1px solid rgba(255,255,255,0.08);
}
</style>
""", unsafe_allow_html=True)

# ======================================================
# Top KPIs (Baseline, Current, Delta)
# ======================================================
k1, k2, k3 = st.columns(3)

k1.metric("Baseline EBITDA", money0(baseline["EBITDA"]))

k2.markdown(
    f"""
    <div class="kpi-card">
        <div class="kpi-label">Current EBITDA</div>
        <div class="kpi-value {value_class(current['EBITDA'])}">
            {money0(current['EBITDA'])}
            <span class="{delta_class(delta_ebitda)}">{arrow(delta_ebitda)}</span>
        </div>
    </div>
    """,
    unsafe_allow_html=True,
)

k3.markdown(
    f"""
    <div class="kpi-card">
        <div class="kpi-label">Δ EBITDA vs Baseline</div>
        <div class="kpi-value {delta_class(delta_ebitda)}">
            {money0(delta_ebitda)}
        </div>
    </div>
    """,
    unsafe_allow_html=True,
)

# ======================================================
# Grouped Table
# ======================================================
FORMULAS = {
    "Revenue": "Unit Price × Net Saleable Tons",
    "Variable cost": "Processed Tons × (Energy + Labor + Other)",
    "Contribution": "Revenue − Variable Cost",
    "Contribution %": "Contribution ÷ Revenue",
    "EBITDA": "Contribution − Fixed Cost",
    "EBITDA %": "EBITDA ÷ Revenue",
    "Var cost / processed ton": "Variable Cost ÷ Processed Tons",
    "Contribution / processed ton": "Contribution ÷ Processed Tons",
}

GROUPS = {
    "Production & Time": [
        "Operating hours",
        "Tons processed",
        "Net saleable tons",
    ],
    "Costs": [
        "Variable cost",
        "Fixed cost",
    ],
    "Financial Results": [
        "Revenue",
        "Contribution",
        "Contribution %",
        "EBITDA",
        "EBITDA %",
    ],
    "Unit Economics": [
        "Var cost / processed ton",
        "Contribution / processed ton",
    ],
}

rows = []

for group, metrics in GROUPS.items():
    rows.append({"Metric": f"<b>{group}</b>", "Baseline": "", "Current": "", "Delta": ""})

    for m in metrics:
        b = baseline[m]
        c = current[m]
        d = c - b

        if m in ["Contribution %", "EBITDA %"]:
            base_str = f"{b:.2f}%"
            curr_str = f"{c:.2f}%"
            delta_str = f"{d:.2f} pts"
        elif m in ["Var cost / processed ton", "Contribution / processed ton"]:
            base_str = money2(b)
            curr_str = money2(c)
            delta_str = money2(d)
        elif m in ["Operating hours", "Tons processed", "Net saleable tons"]:
            base_str = f"{b:,.0f}"
            curr_str = f"{c:,.0f}"
            delta_str = f"{d:,.0f}"
        else:
            base_str = money0(b)
            curr_str = money0(c)
            delta_str = money0(d)

        # Baseline cell includes formula (if defined)
        if m in FORMULAS:
            baseline_display = (
                f"{base_str}"
                f"<div style='font-size:12px; color:#9ca3af; margin-top:4px;'>"
                f"({m} = {FORMULAS[m]})"
                f"</div>"
            )
        else:
            baseline_display = base_str

        rows.append({
            "Metric": m,
            "Baseline": baseline_display,
            "Current": colorize(f"{curr_str} {arrow(d)}", d),
            "Delta": colorize(delta_str, d),
        })


    for m in metrics:
        b = baseline[m]
        c = current[m]
        d = c - b

        if m in ["Contribution %", "EBITDA %"]:
            base_str = f"{b:.2f}%"
            curr_str = f"{c:.2f}%"
            delta_str = f"{d:.2f} pts"
        elif m in ["Var cost / processed ton", "Contribution / processed ton"]:
            base_str = money2(b)
            curr_str = money2(c)
            delta_str = money2(d)
        elif m in ["Operating hours", "Tons processed", "Net saleable tons"]:
            base_str = f"{b:,.0f}"
            curr_str = f"{c:,.0f}"
            delta_str = f"{d:,.0f}"
        else:
            base_str = money0(b)
            curr_str = money0(c)
            delta_str = money0(d)

        rows.append({
            "Metric": m,
            "Baseline": base_str,
            "Current": colorize(f"{curr_str} {arrow(d)}", d),
            "Delta": colorize(delta_str, d),
        })

df = pd.DataFrame(rows)

st.subheader("Baseline vs Current vs Delta")
st.markdown(
    "<div class='big-table'>" + df.to_html(index=False, escape=False) + "</div>",
    unsafe_allow_html=True,
)

with st.expander("Baseline inputs (fixed)"):
    st.write(BASELINE)









