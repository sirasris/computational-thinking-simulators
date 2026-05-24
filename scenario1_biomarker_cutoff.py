import streamlit as st
import numpy as np
import matplotlib.pyplot as plt
from scipy import stats

st.set_page_config(page_title="Diagnostic Test Designer", layout="wide", page_icon="🔬")

# ── Custom CSS ──────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=DM+Serif+Display:ital@0;1&family=DM+Mono:wght@400;500&family=DM+Sans:wght@300;400;500&display=swap');

html, body, [class*="css"] { font-family: 'DM Sans', sans-serif; }

.main { background: #0d1117; }
[data-testid="stAppViewContainer"] { background: #0d1117; }
[data-testid="stSidebar"] { background: #111820; border-right: 1px solid #1e2d3d; }

h1, h2, h3 { font-family: 'DM Serif Display', serif; color: #e8f4f8; }

.metric-card {
    background: linear-gradient(135deg, #111820 0%, #162030 100%);
    border: 1px solid #1e3a5f;
    border-radius: 12px;
    padding: 1.4rem 1.5rem;
    text-align: center;
    margin: 0.3rem 0;
}
.metric-value { font-family: 'DM Mono', monospace; font-size: 2.6rem; font-weight: 500; }
.metric-label { font-size: 0.9rem; letter-spacing: 0.10em; text-transform: uppercase; color: #5a8fa8; margin-top: 0.4rem; }
.good { color: #4ade80; }
.warn { color: #fb923c; }
.bad  { color: #f87171; }

.info-box {
    background: #0f2238;
    border-left: 3px solid #3b82f6;
    padding: 0.8rem 1.2rem;
    border-radius: 0 8px 8px 0;
    font-size: 0.95rem;
    color: #93c5fd;
    margin: 0.5rem 0;
}
.stSlider > div > div > div { background: #1e3a5f !important; }
div[data-testid="metric-container"] { background: transparent; }
</style>
""", unsafe_allow_html=True)

# ── Sidebar: hidden distributions ──────────────────────────────────────────
with st.sidebar:
    st.markdown("## 🔬 Disease Parameters")
    st.markdown('<div class="info-box">System parameters.</div>', unsafe_allow_html=True)
    st.markdown("---")
    st.markdown("**Healthy population**")
    mu_healthy = st.slider("Mean biomarker (healthy)", 0.0, 10.0, 3.0, 0.1)
    sd_healthy = st.slider("SD (healthy)", 0.1, 3.0, 1.0, 0.1)
    st.markdown("**Sick population**")
    mu_sick = st.slider("Mean biomarker (sick)", 0.0, 10.0, 6.5, 0.1)
    sd_sick = st.slider("SD (sick)", 0.1, 3.0, 1.2, 0.1)
    st.markdown("---")
    st.markdown("**Biomarker range**")
    x_min = st.slider("X min", 0.0, 0.0, 5.0, 0.5)
    x_max = st.slider("X max", 10.0, 20.0, 13.0, 0.5)

# ── Main ────────────────────────────────────────────────────────────────────
st.markdown("# 🔬 Diagnostic test designer")
st.markdown("Explore how disease prevalence shapes the performance of diagnostic test")
st.markdown("#### Adjust biomarker threshold to achieve **80% PPV**")

col_thresh, col_prev = st.columns([1, 1])
with col_thresh:
    threshold = st.slider("**Diagnostic threshold** — Biomarker values above this → test positive",
                          float(x_min), float(x_max), (mu_healthy + mu_sick) / 2, 0.05)
with col_prev:
    prevalence = st.select_slider(
        "**Disease prevalence** in the population",
        options=[0.001, 0.005, 0.01, 0.05, 0.10, 0.20, 0.30, 0.50],
        value=0.10,
        format_func=lambda v: f"{v*100:.1f}%"
    )

# ── Compute metrics ─────────────────────────────────────────────────────────
dist_h = stats.norm(mu_healthy, sd_healthy)
dist_s = stats.norm(mu_sick, sd_sick)

sensitivity = 1 - dist_s.cdf(threshold)
specificity = dist_h.cdf(threshold)
fpr         = 1 - specificity

ppv_num = sensitivity * prevalence
ppv_den = sensitivity * prevalence + fpr * (1 - prevalence)
PPV = ppv_num / ppv_den if ppv_den > 0 else 0.0
NPV_num = specificity * (1 - prevalence)
NPV_den = specificity * (1 - prevalence) + (1 - sensitivity) * prevalence
NPV = NPV_num / NPV_den if NPV_den > 0 else 0.0

def color_cls(v, thr_good=0.8, thr_warn=0.6):
    if v >= thr_good: return "good"
    if v >= thr_warn: return "warn"
    return "bad"

# ── Metric cards ─────────────────────────────────────────────────────────────
st.markdown("### 📊 Performance at your selected threshold")
c1, c2, c3, c4 = st.columns(4)
metrics = [
    (c1, "PPV", PPV, "Positive Predictive Value"),
    (c2, "Sensitivity", sensitivity, "True Positive Rate (Sensitivity)"),
    (c3, "Specificity", specificity, "True Negative Rate (Specificity)"),
    (c4, "NPV", NPV, "Negative Predictive Value"),
]
for col, name, val, label in metrics:
    with col:
        cls = color_cls(val)
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-value {cls}">{val:.1%}</div>
            <div class="metric-label">{label}</div>
        </div>""", unsafe_allow_html=True)

if PPV >= 0.80:
    st.success(f"✅ **Target achieved!** PPV ≥ 80% at this threshold with {prevalence*100:.1f}% prevalence.")
else:
    st.warning(f"⚠️ PPV is {PPV:.1%} — below the 80% target. Try raising the threshold.")

# ── Shared plot settings ─────────────────────────────────────────────────────
BG       = '#0d1117'
TICK_CLR = '#5a8fa8'
LABEL_CLR= '#8ba8b8'
TITLE_CLR= '#e8f4f8'
SPINE_CLR= '#1e3a5f'
LGND_FC  = '#111820'

TITLE_FS = 18
LABEL_FS = 16
TICK_FS  = 14
LGND_FS  = 14
ANNOT_FS = 15

x = np.linspace(x_min, x_max, 1000)
ph = dist_h.pdf(x)
ps = dist_s.pdf(x)
mask_pos = x >= threshold

# ── Simulation data (shared) ─────────────────────────────────────────────────
N_sim     = 2000
n_sick    = int(N_sim * prevalence)
n_healthy = N_sim - n_sick
np.random.seed(42)
biomarker_sick    = np.random.normal(mu_sick,    sd_sick,    max(n_sick, 1))
biomarker_healthy = np.random.normal(mu_healthy, sd_healthy, max(n_healthy, 1))
pos_sick    = int(np.sum(biomarker_sick    >= threshold))
pos_healthy = int(np.sum(biomarker_healthy >= threshold))
neg_sick    = n_sick    - pos_sick
neg_healthy = n_healthy - pos_healthy
sim_ppv = pos_sick / (pos_sick + pos_healthy) if (pos_sick + pos_healthy) > 0 else 0

st.markdown("### Impact of your chosen threshold")

# ── Two-panel figure side by side ────────────────────────────────────────────
fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(18, 7), facecolor=BG)
fig.subplots_adjust(left=0.07, right=0.97, top=0.88, bottom=0.13, wspace=0.38)

# ─── Panel 1: Distributions ──────────────────────────────────────────────────
ax1.set_facecolor(BG)
ax1.fill_between(x, ph, alpha=0.22, color='#38bdf8')
ax1.fill_between(x, ps, alpha=0.22, color='#f87171')
ax1.plot(x, ph, color='#38bdf8', lw=2.5, label='Healthy')
ax1.plot(x, ps, color='#f87171', lw=2.5, label='Sick')

ax1.fill_between(x[mask_pos], ps[mask_pos], alpha=0.60, color='#4ade80',
                 label=f'True Positive')
ax1.fill_between(x[mask_pos], ph[mask_pos], alpha=0.45, color='#fb923c',
                 label=f'False Positive')
ax1.axvline(threshold, color='#facc15', lw=3, ls='--',
            label=f'Threshold = {threshold:.2f}')

ax1.set_xlabel('Biomarker Level', color=LABEL_CLR, fontsize=LABEL_FS)
ax1.set_ylabel('Density', color=LABEL_CLR, fontsize=LABEL_FS)
ax1.set_title('Biomarker distribution in each population group',
              color=TITLE_CLR, fontsize=TITLE_FS, pad=12)
ax1.tick_params(colors=TICK_CLR, labelsize=TICK_FS)
for sp in ax1.spines.values(): sp.set_color(SPINE_CLR)
ax1.legend(fontsize=LGND_FS, facecolor=LGND_FC, edgecolor=SPINE_CLR,
           labelcolor='#c8dde8', framealpha=0.9)
ax1.set_xlim(x_min, x_max)

# ─── Panel 2: Patient bar chart ───────────────────────────────────────────────
ax2.set_facecolor(BG)
bar_labels = ['True Positive\n(sick & +ve)', 'False Positive\n(healthy & +ve)',
              'False Negative\n(sick & −ve)', 'True Negative\n(healthy & −ve)']
bar_vals   = [pos_sick, pos_healthy, neg_sick, neg_healthy]
bar_colors = ['#4ade80', '#fb923c', '#f87171', '#38bdf8']

bars = ax2.bar(bar_labels, bar_vals, color=bar_colors, alpha=0.88, width=0.55)
for bar, val in zip(bars, bar_vals):
    ax2.text(bar.get_x() + bar.get_width() / 2,
             bar.get_height() + N_sim * 0.008,
             str(val), ha='center', va='bottom',
             color='#e8f4f8', fontsize=ANNOT_FS, fontweight='bold')

ax2.set_title(f'Simulated population  (N = {N_sim},  Prevalence = {prevalence*100:.1f}%)\n'
              f'Simulated PPV = {sim_ppv:.1%}',
              color=TITLE_CLR, fontsize=TITLE_FS, pad=12, linespacing=1.5)
ax2.set_ylabel('Number of Patients', color=LABEL_CLR, fontsize=LABEL_FS)
ax2.tick_params(colors=TICK_CLR, labelsize=TICK_FS)
for sp in ax2.spines.values(): sp.set_color(SPINE_CLR)
ax2.set_ylim(0, max(bar_vals) * 1.18)

st.pyplot(fig)
plt.close(fig)

# ── Reflection prompts ───────────────────────────────────────────────────────
with st.expander("💬 Reflection Questions"):
    st.markdown("""
    1. **Prevalence effect**: As prevalence decreases, how would you adjust the threshold to achieve ≥80% PPV? Do you understand why?
    2. **Trade-off**: As you raise the threshold to improve PPV, what happens to sensitivity? What does this mean clinically?
    3. **Best threshold**: For each prevalence level, find the *lowest threshold* that still achieves ≥80% PPV. Record these. What pattern do you see?
    4. **Real-world implication**: Suppose this test is used for population-wide screening vs. testing only symptomatic patients. How should the threshold differ?
    """)
