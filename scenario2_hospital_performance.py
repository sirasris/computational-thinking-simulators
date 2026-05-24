import streamlit as st
import numpy as np
 
st.set_page_config(page_title="Hospital performance paradox", layout="wide", page_icon="🏥")
 
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Playfair+Display:wght@700&family=Source+Code+Pro:wght@400;600&family=Nunito:wght@300;400;600&display=swap');
 
html, body, [class*="css"] { font-family: 'Nunito', sans-serif; font-size: 0.95rem; }
[data-testid="stAppViewContainer"] { background: #faf7f2; }
[data-testid="stSidebar"] { background: #f0ebe2; border-right: 1px solid #d6c9b5; }
 
h1 { font-family: 'Playfair Display', serif; color: #2c1810; }
h2, h3 { font-family: 'Playfair Display', serif; color: #3d2515; }
 
.hosp-card {
    border-radius: 12px;
    padding: 1.1rem 1.4rem;
    margin: 0.4rem 0;
    border: 2px solid;
}
.hosp-a { background: #fff8f0; border-color: #e07b39; }
.hosp-b { background: #f0f4ff; border-color: #4a6fa5; }
 
.paradox-banner {
    background: linear-gradient(90deg, #7c3aed, #db2777);
    color: white;
    border-radius: 10px;
    padding: 1.1rem 1.5rem;
    text-align: center;
    font-family: 'Playfair Display', serif;
    font-size: 1.4rem;
    margin: 0.8rem 0;
}
.step-banner {
    border-radius: 10px;
    padding: 0.85rem 1.5rem;
    text-align: center;
    font-size: 1.05rem;
    font-weight: 600;
    margin: 0.8rem 0;
    border: 2px solid;
}
.step-mix  { background: #fff7ed; border-color: #fb923c; color: #9a3412; }
.step-rate { background: #fdf4ff; border-color: #c084fc; color: #6b21a8; }
.step-ok   { background: #f0fdf4; border-color: #4ade80; color: #166534; }
 
/* ── Table styles ── */
.tbl {
    width: 100%;
    border-collapse: collapse;
    font-family: 'Source Code Pro', monospace;
    font-size: 0.88rem;
}
.tbl th {
    padding: 0.45rem 0.6rem;
    text-align: center;
    font-size: 0.78rem;
    letter-spacing: 0.05em;
    text-transform: uppercase;
}
.tbl-a th { background: #7c3418; color: #fff8f0; }
.tbl-b th { background: #1e3a6e; color: #f0f4ff; }
.tbl-w th { background: #3d3d3d; color: #f5f5f5; }
.tbl td {
    padding: 0.42rem 0.6rem;
    text-align: center;
    border-bottom: 1px solid #d6c9b5;
    font-size: 0.88rem;
}
.tbl-a tr:nth-child(even) td { background: #fff0e4; }
.tbl-b tr:nth-child(even) td { background: #e8eeff; }
.tbl td:first-child { text-align: left; font-weight: 600; }
.overall-row td { font-weight: 700; font-size: 0.92rem; border-top: 2px solid #aaa; }
.win  { color: #16a34a; font-weight: 700; }
.lose { color: #dc2626; font-weight: 700; }
.neutral { color: #555; }
.calc { color: #888; font-size: 0.78rem; }
</style>
""", unsafe_allow_html=True)
 
st.markdown("# 🏥 Hospital performance paradox")
st.markdown("#### Can a hospital provide better care in every patient group, yet appear worse overall?")
 
# ── Sidebar controls ──────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("## ⚙️ Hospital Settings")
    st.markdown("---")
    st.markdown("### 🏨 Hospital A — Performance")
    p_A_mild   = st.slider("Success rate: Mild patients",   0.0, 1.0, 0.90, 0.01, key='pAm')
    p_A_severe = st.slider("Success rate: Severe patients", 0.0, 1.0, 0.50, 0.01, key='pAs')
    st.markdown("### 🏨 Hospital B — Performance")
    p_B_mild   = st.slider("Success rate: Mild patients",   0.0, 1.0, 0.80, 0.01, key='pBm')
    p_B_severe = st.slider("Success rate: Severe patients", 0.0, 1.0, 0.40, 0.01, key='pBs')
    st.markdown("---")
    st.markdown("### 👥 Patient Mix")
    st.markdown("**Hospital B** always receives 50% mild / 50% severe patients.")
    prop_mild_A = st.slider("Hospital A — proportion of mild patients",
                            0.0, 1.0, 0.50, 0.01,
                            help="0.0 = all severe, 1.0 = all mild",
                            key='propA')
    total_A = st.slider("Total patients — Hospital A", 50, 2000, 500, 50)
    total_B = st.slider("Total patients — Hospital B", 50, 2000, 500, 50)
 
# ── Compute ───────────────────────────────────────────────────────────────────
n_A_mild   = round(total_A * prop_mild_A)
n_A_severe = total_A - n_A_mild
 
n_B_mild   = total_B // 2
n_B_severe = total_B - n_B_mild
 
s_A_mild   = p_A_mild   * n_A_mild
s_A_severe = p_A_severe * n_A_severe
s_B_mild   = p_B_mild   * n_B_mild
s_B_severe = p_B_severe * n_B_severe
 
total_cured_A = s_A_mild + s_A_severe
total_cured_B = s_B_mild + s_B_severe
overall_A = total_cured_A / total_A if total_A > 0 else 0.0
overall_B = total_cured_B / total_B if total_B > 0 else 0.0
 
A_beats_mild      = p_A_mild   > p_B_mild
A_beats_severe    = p_A_severe > p_B_severe
A_better_subgroups = A_beats_mild and A_beats_severe
A_worse_overall    = overall_A < overall_B
paradox_achieved   = A_better_subgroups and A_worse_overall
 
# ── Status banner ─────────────────────────────────────────────────────────────
if paradox_achieved:
    st.markdown(
        '<div class="paradox-banner">'
        '🎉 Simpson\'s Paradox achieved! '
        'Hospital A is better in <em>both</em> groups — yet appears worse overall!'
        '</div>', unsafe_allow_html=True)
else:
    st.markdown(
        '<div class="step-banner step-rate">'
        '⚙️ Adjust the patient mix so that Hospital A is better in <em>both</em> groups — yet appears worse overall.'
        '</div>', unsafe_allow_html=True)
 
# ── Helper: format cured count nicely ────────────────────────────────────────
def fmt(n):
    return str(int(round(n)))
 
def winner_cell(a_beats):
    if a_beats:
        return '<span class="win">🏥 A</span>'
    else:
        return '<span class="lose">🏥 B</span>'
 
# ── Single unified comparison table ──────────────────────────────────────────
overall_winner = winner_cell(overall_A >= overall_B)
 
st.markdown(f"""
<table class="tbl">
  <tr>
    <th class="tbl-w" style="text-align:left">Group</th>
    <th class="tbl-a" colspan="3">🏥 Hospital A</th>
    <th class="tbl-b" colspan="3">🏥 Hospital B</th>
    <th class="tbl-w">Winner</th>
  </tr>
  <tr>
    <th style="text-align:left; background:#f5f0e8"></th>
    <th class="tbl-a">Patients</th>
    <th class="tbl-a">Cured</th>
    <th class="tbl-a">Rate</th>
    <th class="tbl-b">Patients</th>
    <th class="tbl-b">Cured</th>
    <th class="tbl-b">Rate</th>
    <th class="tbl-w"></th>
  </tr>
  <tr>
    <td>Mild</td>
    <td>{n_A_mild}</td>
    <td>{fmt(s_A_mild)}</td>
    <td>{p_A_mild:.1%}</td>
    <td>{n_B_mild}</td>
    <td>{fmt(s_B_mild)}</td>
    <td>{p_B_mild:.1%}</td>
    <td>{winner_cell(A_beats_mild)}</td>
  </tr>
  <tr>
    <td>Severe</td>
    <td>{n_A_severe}</td>
    <td>{fmt(s_A_severe)}</td>
    <td>{p_A_severe:.1%}</td>
    <td>{n_B_severe}</td>
    <td>{fmt(s_B_severe)}</td>
    <td>{p_B_severe:.1%}</td>
    <td>{winner_cell(A_beats_severe)}</td>
  </tr>
  <tr class="overall-row">
    <td>Overall</td>
    <td>{total_A}</td>
    <td>{fmt(total_cured_A)}</td>
    <td><strong>{overall_A:.1%}</strong> <span class="calc">= {fmt(total_cured_A)}/{total_A}</span></td>
    <td>{total_B}</td>
    <td>{fmt(total_cured_B)}</td>
    <td><strong>{overall_B:.1%}</strong> <span class="calc">= {fmt(total_cured_B)}/{total_B}</span></td>
    <td>{overall_winner}</td>
  </tr>
</table>
""", unsafe_allow_html=True)
 
# ── Reflection questions ──────────────────────────────────────────────────────
with st.expander("💬 Why does this happen? — Reflection Questions"):
    prop_A_display = f"{prop_mild_A*100:.0f}% mild"
    prop_B_display = f"{n_B_mild/(n_B_mild+n_B_severe)*100:.0f}% mild"
    st.markdown(f"""
    1. Which variable is the "confounder" here — the hidden factor that distorts the overall comparison?
    2. If you were a patient, which hospital would you *actually* prefer? Why?
    4. **Find the boundary**: At the current treatment rates, what proportion of mild patients must Hospital A receive before the paradox disappears?
    5. How does the difference in actual treatment performance affect the boundary? If Hospital A is so much better than Hospital B, can the paradox still appear?
    """)