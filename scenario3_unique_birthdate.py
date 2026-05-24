import streamlit as st
import numpy as np
import pandas as pd
from datetime import date, timedelta
import random

st.set_page_config(page_title="Patient birthdate uniqueness rate", layout="wide", page_icon="🔒")

# ── CSS ───────────────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Share+Tech+Mono&family=Syne:wght@400;700;800&family=Syne+Mono&display=swap');

html, body, [class*="css"] {
    font-family: 'Syne', sans-serif;
    background: #0a0e0a;
    color: #c8d5c8;
}
[data-testid="stAppViewContainer"] { background: #0a0e0a; }
[data-testid="stSidebar"] {
    background: #0d120d;
    border-right: 1px solid #1f3320;
}

h1 { font-family: 'Syne', sans-serif; font-weight: 800; color: #7fff7f; letter-spacing: -0.02em; }
h2, h3 { font-family: 'Syne', sans-serif; font-weight: 700; color: #a8c5a8; }

/* Metric cards */
.metric-grid { display: flex; gap: 1rem; margin: 1rem 0; }
.metric-box {
    flex: 1;
    background: #0d160d;
    border: 1px solid #1f3320;
    border-radius: 4px;
    padding: 1rem 1.2rem;
    font-family: 'Share Tech Mono', monospace;
}
.metric-box .val {
    font-size: 2.4rem;
    font-weight: 700;
    line-height: 1;
    margin-bottom: 0.25rem;
}
.metric-box .lbl {
    font-size: 0.72rem;
    letter-spacing: 0.1em;
    text-transform: uppercase;
    color: #4a6e4a;
}
.green  { color: #7fff7f; }
.amber  { color: #ffbf00; }
.red    { color: #ff5555; }
.dim    { color: #4a6e4a; }

/* Stage headers */
.stage-header {
    font-family: 'Share Tech Mono', monospace;
    font-size: 0.72rem;
    letter-spacing: 0.2em;
    text-transform: uppercase;
    color: #4a6e4a;
    border-bottom: 1px solid #1f3320;
    padding-bottom: 0.4rem;
    margin-bottom: 1rem;
}

/* Target band */
.target-box {
    background: #0d160d;
    border: 1px solid #2a5c2a;
    border-left: 4px solid #7fff7f;
    border-radius: 0 4px 4px 0;
    padding: 0.8rem 1.2rem;
    font-family: 'Share Tech Mono', monospace;
    font-size: 0.9rem;
    margin: 0.8rem 0;
    color: #a8c5a8;
}
.warn-box {
    background: #160d00;
    border: 1px solid #5c3a00;
    border-left: 4px solid #ffbf00;
    border-radius: 0 4px 4px 0;
    padding: 0.8rem 1.2rem;
    font-family: 'Share Tech Mono', monospace;
    font-size: 0.9rem;
    margin: 0.8rem 0;
    color: #c8a870;
}
.breach-box {
    background: #160000;
    border: 1px solid #5c0000;
    border-left: 4px solid #ff5555;
    border-radius: 0 4px 4px 0;
    padding: 0.8rem 1.2rem;
    font-family: 'Share Tech Mono', monospace;
    font-size: 0.9rem;
    margin: 0.8rem 0;
    color: #c87070;
}

/* Patient record table */
.rec-table {
    width: 100%;
    border-collapse: collapse;
    font-family: 'Share Tech Mono', monospace;
    font-size: 0.83rem;
}
.rec-table th {
    background: #111a11;
    color: #4a6e4a;
    padding: 0.4rem 0.7rem;
    text-align: left;
    font-size: 0.68rem;
    letter-spacing: 0.12em;
    text-transform: uppercase;
    border-bottom: 1px solid #1f3320;
}
.rec-table td {
    padding: 0.32rem 0.7rem;
    border-bottom: 1px solid #111a11;
    color: #a8c5a8;
}
.rec-table tr.collision td {
    background: #1a0a00;
    color: #ffbf00;
    font-weight: 700;
}
.rec-table tr.collision-first td {
    background: #1a0000;
    color: #ff5555;
    font-weight: 700;
}
.badge {
    display: inline-block;
    font-size: 0.65rem;
    padding: 0.1rem 0.4rem;
    border-radius: 2px;
    letter-spacing: 0.08em;
}
.badge-collision { background: #3a1a00; color: #ffbf00; border: 1px solid #5c3a00; }
.badge-match     { background: #3a0000; color: #ff5555; border: 1px solid #5c0000; }

/* Probability curve */
.prob-hint {
    font-family: 'Share Tech Mono', monospace;
    font-size: 0.78rem;
    color: #4a6e4a;
    margin-top: 0.5rem;
}

/* Slider label override */
.stSlider label { font-family: 'Share Tech Mono', monospace !important; color: #7fff7f !important; }

div[data-testid="stExpander"] {
    border: 1px solid #1f3320 !important;
    border-radius: 4px;
    background: #0d120d;
}
</style>
""", unsafe_allow_html=True)

# ── Constants ─────────────────────────────────────────────────────────────────
YEAR = 1970
# 1970 was not a leap year
ALL_DATES = [date(YEAR, m, d)
             for m in range(1, 13)
             for d in range(1, [31,28,31,30,31,30,31,31,30,31,30,31][m-1]+1)]
N_DAYS = len(ALL_DATES)   # 365

def exact_collision_prob(n):
    """P(at least one shared birthday) = 1 - P(all distinct)."""
    if n > N_DAYS:
        return 1.0
    p_none = 1.0
    for k in range(n):
        p_none *= (N_DAYS - k) / N_DAYS
    return 1.0 - p_none

def sim_collision_prob(n, n_sims=5000, seed=42):
    rng = np.random.default_rng(seed)
    hits = 0
    for _ in range(n_sims):
        sample = rng.integers(0, N_DAYS, size=n)
        if len(np.unique(sample)) < n:
            hits += 1
    return hits / n_sims

# ── Header ────────────────────────────────────────────────────────────────────
st.markdown("# 🔒 Patient birthdate uniqueness rate")
st.markdown(
    "**Scenario:** An AIDS clinic experienced a data breach. "
    "Records for **N patients born in 1970** were leaked, indexed only by date of birth. "
)
st.markdown(
    "If two patients share the same birth date, their HIV test results may be **safely masked**. "
    "How many patients does it take before this event becomes very likely?"
)

st.markdown("---")

# ═══════════════════════════════════════════════════════════════════════════════
# STAGE 1 — Find the threshold N
# ═══════════════════════════════════════════════════════════════════════════════
st.markdown('<div class="stage-header">▸ Stage 1 — Find the thresholds</div>', unsafe_allow_html=True)

col_left, col_right = st.columns([1, 1], gap="large")

with col_left:
    st.markdown("**Your mission:** Find the smallest number of patients **N** such that the probability of at least one common birthdate  reaches the target.")

    target_pct = st.select_slider(
        "Probability target",
        options=[50, 75, 90, 95, 99],
        value=50,
        format_func=lambda v: f"{v}%",
        key="target"
    )
    target = target_pct / 100

    n_guess = st.slider(
        "Your guess for N (number of patients in the leaked batch)",
        min_value=1, max_value=80, value=5, step=1, key="n_guess"
    )

    prob_exact = exact_collision_prob(n_guess)
    prob_sim   = sim_collision_prob(n_guess)

    # Metric cards
    st.markdown(f"""
    <div class="metric-grid">
      <div class="metric-box">
        <div class="val {'green' if prob_exact >= target else 'amber'}">{prob_exact:.1%}</div>
        <div class="lbl">Exact probability</div>
      </div>
      <div class="metric-box">
        <div class="val {'green' if prob_sim >= target else 'amber'}">{prob_sim:.1%}</div>
        <div class="lbl">Simulated (5 000 runs)</div>
      </div>
      <div class="metric-box">
        <div class="val dim">{N_DAYS}</div>
        <div class="lbl">Possible birth dates</div>
      </div>
    </div>
    """, unsafe_allow_html=True)

    if prob_exact >= target:
        st.markdown(
            f'<div class="target-box">✔ N = {n_guess} achieves {prob_exact:.1%} collision probability — '
            f'above your {target_pct}% target.</div>',
            unsafe_allow_html=True)
    else:
        gap = target - prob_exact
        st.markdown(
            f'<div class="warn-box">✘ N = {n_guess} gives {prob_exact:.1%} — '
            f'still {gap:.1%} below the {target_pct}% target. Try increasing N.</div>',
            unsafe_allow_html=True)

with col_right:
    # Draw probability curve with matplotlib
    import matplotlib.pyplot as plt
    import matplotlib.ticker as mticker

    ns = np.arange(1, 121)
    probs = [exact_collision_prob(n) for n in ns]

    fig, ax = plt.subplots(figsize=(6, 4), facecolor='#0a0e0a')
    ax.set_facecolor('#0a0e0a')

    ax.plot(ns, probs, color='#7fff7f', lw=2.2)
    ax.axhline(target, color='#ffbf00', lw=1.2, ls='--', alpha=0.8,
               label=f'{target_pct}% target')
    ax.axvline(n_guess, color='#ff5555', lw=1.2, ls=':', alpha=0.9,
               label=f'N = {n_guess}')
    ax.scatter([n_guess], [prob_exact], color='#ff5555', s=55, zorder=5)

    # shade the region above target on the curve
    ax.fill_between(ns, probs, target,
                    where=[p >= target for p in probs],
                    alpha=0.12, color='#7fff7f')

    ax.set_xlabel('Number of patients N', color='#4a6e4a', fontsize=10)
    ax.set_ylabel('P(at least one shared birth date)', color='#4a6e4a', fontsize=10)
    ax.set_title('Collision Probability vs Patient Count', color='#a8c5a8', fontsize=11)
    ax.tick_params(colors='#4a6e4a', labelsize=9)
    ax.yaxis.set_major_formatter(mticker.PercentFormatter(xmax=1))
    for sp in ax.spines.values(): sp.set_color('#1f3320')
    ax.legend(fontsize=9, facecolor='#0d120d', edgecolor='#1f3320', labelcolor='#a8c5a8')
    ax.set_xlim(1, 120)
    ax.set_ylim(-0.02, 1.05)
    ax.grid(axis='y', color='#1a2a1a', lw=0.6)

    st.pyplot(fig, use_container_width=True)
    plt.close(fig)

    st.markdown(
        f'<div class="prob-hint">'
        f'The curve reaches 50% at N ≈ 23, and 99% at N ≈ 57.<br>'
        f'The exact formula: P(collision) = 1 − (365 × 364 × … × (365−N+1)) / 365ᴺ'
        f'</div>',
        unsafe_allow_html=True)

st.markdown("---")

# ═══════════════════════════════════════════════════════════════════════════════
# STAGE 2 — Generate and inspect a random patient batch
# ═══════════════════════════════════════════════════════════════════════════════
st.markdown('<div class="stage-header">▸ Stage 2 — Inspect a Random Patient Batch</div>', unsafe_allow_html=True)

st.markdown(
    "Generate a random batch of N patients and inspect their birth dates. "
    "Rows highlighted in **<span style='color:#ff5555'>red</span>** are the first occurrence of a repeated birth date; "
    "rows in **<span style='color:#ffbf00'>amber</span>** are subsequent matches.",
    unsafe_allow_html=True
)

col_s2a, col_s2b = st.columns([1, 2], gap="large")

with col_s2a:
    n_stage2 = st.slider(
        "Batch size N for simulation",
        min_value=1, max_value=100, value=n_guess, step=1, key="n_stage2"
    )
    seed_val = st.number_input("Random seed (change to get a new batch)", min_value=0, max_value=9999,
                                value=42, step=1, key="seed2")
    run_sim = st.button("⟳ Generate new patient batch", use_container_width=True)

    # Probability reminder
    p2 = exact_collision_prob(n_stage2)
    clr = 'green' if p2 >= 0.5 else 'amber'
    st.markdown(f"""
    <div class="metric-grid" style="margin-top:1rem">
      <div class="metric-box">
        <div class="val {clr}">{p2:.1%}</div>
        <div class="lbl">Repeated birthdate probability at N={n_stage2}</div>
      </div>
    </div>
    """, unsafe_allow_html=True)

with col_s2b:
    # Generate patient records
    rng = np.random.default_rng(int(seed_val) + (1 if run_sim else 0))
    
    FIRST_NAMES = ["Alex","Jordan","Morgan","Taylor","Casey","Riley","Drew","Quinn",
                   "Avery","Blake","Cameron","Dakota","Emery","Finley","Hayden",
                   "Jamie","Kendall","Logan","Micah","Parker","Reese","Sage","Skylar"]
    LAST_NAMES  = ["Smith","Johnson","Lee","Brown","Davis","Wilson","Moore","Taylor",
                   "Anderson","Thomas","Jackson","White","Harris","Martin","Garcia",
                   "Martinez","Robinson","Clark","Lewis","Walker","Hall","Young","Allen"]

    rng2 = np.random.default_rng(int(seed_val))
    chosen_dates = rng2.choice(N_DAYS, size=n_stage2, replace=True)
    birth_dates  = [ALL_DATES[i] for i in chosen_dates]

    fn = rng2.choice(FIRST_NAMES, size=n_stage2)
    ln = rng2.choice(LAST_NAMES,  size=n_stage2)

    # Build patient IDs
    patient_ids = [f"PAT-1970-{i+1:04d}" for i in range(n_stage2)]

    # HIV result (random, just for narrative)
    results = rng2.choice(["Negative", "Positive"], size=n_stage2, p=[0.85, 0.15])

    df = pd.DataFrame({
        "Patient ID":   patient_ids,
        "Name":         [f"{f} {l}" for f, l in zip(fn, ln)],
        "Date of Birth": [d.strftime("%d %b 1970") for d in birth_dates],
        "_dob_key":     [d.strftime("%m-%d") for d in birth_dates],
        "HIV Result":   results,
    })

    # Find collisions
    dob_counts  = df["_dob_key"].value_counts()
    colliding   = set(dob_counts[dob_counts > 1].index)

    # Mark rows: first occurrence = 'collision-first', subsequent = 'collision'
    seen = {}
    row_classes = []
    for _, row in df.iterrows():
        k = row["_dob_key"]
        if k in colliding:
            if k not in seen:
                seen[k] = True
                row_classes.append("collision-first")
            else:
                row_classes.append("collision")
        else:
            row_classes.append("")

    n_collisions = len(colliding)
    n_affected   = sum(1 for c in row_classes if c)

    # Summary
    if n_collisions > 0:
        st.markdown(
            f'<div class="breach-box">⚠ REPEATED BIRTHDATE DETECTED — {n_collisions} birth date(s) shared '
            f'across {n_affected} patient records.</div>',
            unsafe_allow_html=True)
    else:
        st.markdown(
            '<div class="target-box">✔ No repetition in this batch — all birth dates are unique.</div>',
            unsafe_allow_html=True)

    # Render table
    rows_html = ""
    for i, (_, row) in enumerate(df.iterrows()):
        cls = row_classes[i]
        dob_str = row["Date of Birth"]
        badge   = ""
        if cls == "collision-first":
            badge = ' <span class="badge badge-match">FIRST MATCH</span>'
        elif cls == "collision":
            badge = ' <span class="badge badge-collision">REPEATED</span>'

        result_color = "red" if row["HIV Result"] == "Positive" else "dim"
        result_str   = f'<span class="{result_color}">{row["HIV Result"]}</span>'

        rows_html += f"""
        <tr class="{cls}">
          <td>{row['Patient ID']}</td>
          <td>{row['Name']}</td>
          <td>{dob_str}{badge}</td>
          <td>{result_str}</td>
        </tr>"""

    st.markdown(f"""
    <div style="max-height: 420px; overflow-y: auto; border: 1px solid #1f3320; border-radius: 4px;">
    <table class="rec-table">
      <thead>
        <tr>
          <th>Patient ID</th>
          <th>Name</th>
          <th>Date of Birth</th>
          <th>HIV Result</th>
        </tr>
      </thead>
      <tbody>{rows_html}</tbody>
    </table>
    </div>
    """, unsafe_allow_html=True)

    st.markdown(
        f'<div class="prob-hint" style="margin-top:0.6rem">'
        f'Batch: {n_stage2} patients · {n_collisions} shared birth date(s) · {n_affected} affected records'
        f'</div>', unsafe_allow_html=True)

st.markdown("---")

# ── Reflection ────────────────────────────────────────────────────────────────
with st.expander("💬 Reflection Questions"):
    st.markdown("""
    1. **Intuition check:** Before trying the slider, how many patients did you *expect* would be needed to reach 50% collision probability? Were you surprised by the answer?
    2. **The paradox:** There are 365 possible birth dates, yet collisions become likely with far fewer than 365 patients. Why?
    3. **Real-world stakes:** In this scenario, a collision means one patient's HIV result could be attributed to another. What are the human consequences of a false positive? A false negative?
    4. **Scaling up:** Hospitals store records indexed by date of birth *and* year of birth (so ~36,500 possible keys for patients across a century). How would you expect the threshold N to change?
    5. **Design fix:** As a data engineer, how would you redesign the record system to make collisions impossible, regardless of N?
    """)
