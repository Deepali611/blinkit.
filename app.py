import streamlit as st
import pandas as pd
import requests
import json
import re

st.set_page_config(page_title="Blinkit Discovery Intelligence", layout="wide", page_icon="◆")

# =========================================================
# TOKENS — warm off-white, charcoal, restrained Blinkit yellow
# =========================================================
BG = "#FBF9F4"; CARD = "#FFFFFF"; INK = "#2B2A28"; MUTED = "#77746D"; LINE = "#EAE6DC"
YELLOW = "#F8CB46"; YELLOW_BG = "#FFF8E3"; YELLOW_BORDER = "#EFDC9E"
GREEN = "#1E8E5A"; GREEN_BG = "#EBF7F1"
RED = "#C63B2E"; RED_BG = "#FBEBE9"
GREY_BG = "#F3F1EA"

REASON_COLORS = {"trust": RED, "price": "#4F5FBF", "convenience": GREEN,
                  "no_discovery": "#7C5CBF", "habit": MUTED, "other": "#B4AF9F"}
SEGMENT_COLORS = {"one_time_complainer": MUTED, "quality_focused": RED,
                   "price_sensitive": "#4F5FBF", "unclear": "#B4AF9F", "heavy_user": GREEN,
                   "light_new_user": "#7C5CBF", "senior_citizen": "#B8860B"}

st.markdown(f"""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');
.stApp {{ background: {BG}; }}
html, body, [class*="css"] {{ font-family: 'Inter', sans-serif; color: {INK}; }}
#MainMenu, footer, header {{visibility:hidden;}}
section[data-testid="stSidebar"] {{ background:{CARD}; border-right:1px solid {LINE}; }}
section[data-testid="stSidebar"] .stRadio label {{ font-size:13.5px; padding:3px 0; }}

.pagetitle {{ font-size:27px; font-weight:700; margin:0 0 2px; letter-spacing:-.3px; }}
.pagesub {{ color:{MUTED}; font-size:13.5px; margin-bottom:20px; }}

.card {{ background:{CARD}; border:1px solid {LINE}; border-radius:12px; padding:20px 22px;
         margin-bottom:14px; box-shadow:0 1px 3px rgba(43,42,40,.04); }}

.aicard {{ background:{CARD}; border:1px solid {LINE}; border-radius:12px; padding:20px 22px;
           margin-bottom:16px; box-shadow:0 1px 3px rgba(43,42,40,.04); }}
.ai-kicker {{ display:flex; align-items:center; gap:8px; margin-bottom:10px; }}
.ai-badge {{ font-size:10px; font-weight:800; letter-spacing:.06em; text-transform:uppercase;
             background:{YELLOW_BG}; color:#8A6A0F; border:1px solid {YELLOW_BORDER}; border-radius:5px; padding:3px 8px; }}
.ai-summary {{ font-size:16px; font-weight:600; line-height:1.4; margin-bottom:10px; }}
.ai-meta-row {{ display:flex; gap:18px; flex-wrap:wrap; font-size:12px; color:{MUTED}; margin-bottom:10px; padding-bottom:10px; border-bottom:1px solid {LINE}; }}
.ai-meta-row b {{ color:{INK}; }}
.conf-badge {{ font-size:10.5px; font-weight:800; padding:2px 8px; border-radius:5px; }}
.section-lbl {{ font-size:10.5px; font-weight:800; color:{MUTED}; text-transform:uppercase; letter-spacing:.05em; margin:10px 0 4px; }}
.section-txt {{ font-size:13px; line-height:1.5; margin-bottom:2px; }}
.pm-strip {{ background:{YELLOW_BG}; border-left:3px solid {YELLOW}; border-radius:0 8px 8px 0; padding:9px 13px; font-size:13px; margin-top:6px; }}
.impact-strip {{ background:{GREEN_BG}; border-left:3px solid {GREEN}; border-radius:0 8px 8px 0; padding:9px 13px; font-size:13px; margin-top:6px; }}
.action-strip {{ background:{GREY_BG}; border-left:3px solid {INK}; border-radius:0 8px 8px 0; padding:9px 13px; font-size:13px; margin-top:6px; }}

.metric-card {{ background:{CARD}; border:1px solid {LINE}; border-radius:12px; padding:15px 17px; box-shadow:0 1px 3px rgba(43,42,40,.04); }}
.metric-card .mlabel {{ font-size:11.5px; color:{MUTED}; font-weight:600; }}
.metric-card .mvalue {{ font-size:27px; font-weight:800; margin-top:4px; letter-spacing:-.5px; }}
.metric-card .mnote {{ font-size:11.5px; color:{MUTED}; margin-top:3px; }}

.row {{ display:flex; align-items:center; gap:10px; padding:6px 0; }}
.dot {{ width:8px; height:8px; border-radius:2px; flex-shrink:0; }}
.rlabel {{ font-size:13px; width:170px; flex-shrink:0; }}
.rbar-track {{ flex:1; height:7px; background:{GREY_BG}; border-radius:4px; overflow:hidden; }}
.rbar-fill {{ height:7px; border-radius:4px; }}
.rval {{ font-size:12.5px; color:{MUTED}; width:110px; text-align:right; flex-shrink:0; }}
.rval b {{ color:{INK}; }}

.opp-card {{ background:{CARD}; border:1px solid {LINE}; border-radius:12px; padding:18px 20px; margin-bottom:12px; box-shadow:0 1px 3px rgba(43,42,40,.04); }}
.badge {{ display:inline-block; font-size:10.5px; font-weight:700; padding:3px 9px; border-radius:5px; margin-right:6px; }}
.evrow {{ border-bottom:1px solid {LINE}; padding:9px 0; font-size:13px; }}
.stepflow {{ display:flex; align-items:center; gap:0; flex-wrap:wrap; margin:10px 0; }}
.stepbox {{ background:{CARD}; border:1px solid {LINE}; border-radius:10px; padding:10px 14px; font-size:12px; font-weight:600; }}
.steparrow {{ color:{MUTED}; padding:0 8px; }}
</style>
""", unsafe_allow_html=True)

@st.cache_data
def load_data():
    df = pd.read_csv("tagged_reviews.csv")
    def bucket_info(text):
        if pd.isna(text) or text in ("none", "not stated"): return None
        t = text.lower()
        if any(k in t for k in ["authentic","seller verif","condition guarantee","seal","ingredient","quality rec","quality assurance"]): return "Authenticity & quality guarantee"
        if any(k in t for k in ["expiry","tamper","cold-chain","packaging","delivery time guarantee","weatherproof"]): return "Packaging & delivery integrity"
        if any(k in t for k in ["price","fee","mrp","tax","surge","billing"]): return "Pricing transparency"
        if any(k in t for k in ["return","replace","refund","cancellation","compensation","promo","substitution","order edit"]): return "Return & refund reliability"
        if any(k in t for k in ["stock","catalog","assortment","sku","variant","coupon","incentive"]): return "Stock & catalog accuracy"
        if any(k in t for k in ["payment","wallet","cod","upi","permission","accountability"]): return "Payment & platform trust"
        if any(k in t for k in ["interface","feature awareness","search","cart","elderly","serviceability","coverage","order-mod"]): return "Discovery & usability"
        return "Other"
    df["info_bucket"] = df["info_needed"].apply(bucket_info)
    return df

df = load_data()
TOTAL_REVIEWS = 1176
N = len(df)
CONF_MAP = {"high": 1, "med": 0.6, "low": 0.3}

def m_discovery_barrier(): return df["reason_type"].isin(["trust","price"]).sum()/N*100
def m_trust_gap(): return (df["reason_type"]=="trust").sum()/N*100
def m_habit_score(): return (df["reason_type"]=="habit").sum()/N*100
def m_exploration_intent(): return df["info_bucket"].notna().sum()/N*100
def m_insight_confidence(): return df["confidence"].map(CONF_MAP).mean()*100
def m_review_coverage(): return N/TOTAL_REVIEWS*100
def m_theme_saturation(): return df["category_mentioned"].nunique()
def m_readiness():
    heavy = df[df["user_segment"]=="heavy_user"]
    if len(heavy)==0: return 0
    return 100 - heavy["reason_type"].isin(["trust","price"]).sum()/len(heavy)*100

def metric_card(label, value, note=""):
    st.markdown(f"""<div class="metric-card"><div class="mlabel">{label}</div>
    <div class="mvalue">{value}</div><div class="mnote">{note}</div></div>""", unsafe_allow_html=True)

def bar_list(counts: dict, colors: dict, unit="mentions"):
    total = sum(counts.values()) or 1
    max_c = max(counts.values()) if counts else 1
    html = ""
    for label, c in sorted(counts.items(), key=lambda x: -x[1]):
        color = colors.get(label, "#B4AF9F")
        pct = c/total*100; width = c/max_c*100
        html += f"""<div class="row"><span class="dot" style="background:{color}"></span>
        <span class="rlabel">{str(label).replace('_',' ')}</span>
        <span class="rbar-track"><span class="rbar-fill" style="width:{width}%;background:{color}"></span></span>
        <span class="rval"><b>{c}</b> {unit} ({pct:.0f}%)</span></div>"""
    return html

def ai_insight_card(summary, confidence, evidence_n, sources, reasoning, validation, pm_implication, business_impact, recommended_action, chart_html=None):
    conf_colors = {"High": (GREEN, GREEN_BG), "Medium": ("#8A6A0F", YELLOW_BG), "Low": (MUTED, GREY_BG)}
    cc, cbg = conf_colors.get(confidence, (MUTED, GREY_BG))
    st.markdown(f"""<div class="aicard">
    <div class="ai-kicker"><span class="ai-badge">AI Growth Analyst</span>
    <span class="conf-badge" style="background:{cbg};color:{cc}">CONFIDENCE: {confidence.upper()}</span></div>
    <div class="ai-summary">{summary}</div>
    <div class="ai-meta-row"><span><b>{evidence_n}</b> supporting reviews</span><span>Sources: <b>{sources}</b></span></div>
    """, unsafe_allow_html=True)
    if chart_html:
        st.markdown(chart_html, unsafe_allow_html=True)
    st.markdown(f"""<div class="section-lbl">Reasoning</div><div class="section-txt">{reasoning}</div>
    <div class="section-lbl">Validation</div><div class="section-txt">{validation}</div>
    <div class="pm-strip"><b>PM implication:</b> {pm_implication}</div>
    <div class="impact-strip"><b>Business impact:</b> {business_impact}</div>
    <div class="action-strip"><b>Recommended action:</b> {recommended_action}</div>
    </div>""", unsafe_allow_html=True)

# =========================================================
# SIDEBAR — product-native navigation
# =========================================================
st.sidebar.markdown(f"""<div style="padding:16px 6px 12px;border-bottom:1px solid {LINE};margin-bottom:8px;">
<div style="font-weight:800;font-size:15.5px;">◆ Discovery Intelligence</div>
<div style="font-size:11.5px;color:{MUTED};margin-top:2px;">Blinkit Growth · AI Discovery Engine</div></div>""", unsafe_allow_html=True)

PAGES = ["Executive Briefing", "Discovery Pipeline", "Behavior Intelligence", "Growth Intelligence",
         "Evidence Explorer", "Opportunity Workspace", "AI Validation", "Live Analysis", "Settings"]
page = st.sidebar.radio("", PAGES, label_visibility="collapsed")
st.sidebar.markdown("---")
st.sidebar.caption(f"{N} validated signals · {TOTAL_REVIEWS:,} reviews scanned")

# =========================================================
# EXECUTIVE BRIEFING
# =========================================================
if page == "Executive Briefing":
    st.markdown('<div class="pagetitle">Executive Briefing</div>', unsafe_allow_html=True)
    st.markdown('<div class="pagesub">Growth Intelligence on cross-category discovery — everything below ties back to one goal: growing the share of customers exploring beyond their usual categories.</div>', unsafe_allow_html=True)

    c1,c2,c3,c4 = st.columns(4)
    with c1: metric_card("Discovery Barrier Index", f"{m_discovery_barrier():.0f}%", "signal driven by trust or price risk")
    with c2: metric_card("Trust Gap Score", f"{m_trust_gap():.0f}%", "signal citing trust/quality risk")
    with c3: metric_card("Shopping Habit Score", f"{m_habit_score():.0f}%", "signal attributable to habit")
    with c4: metric_card("Customer Exploration Intent", f"{m_exploration_intent():.0f}%", "customers naming a specific ask")

    c5,c6,c7,c8 = st.columns(4)
    with c5: metric_card("Discovery Opportunity Readiness", f"{m_readiness():.0f}%", "heavy users clear of trust/price blockers")
    with c6: metric_card("Insight Confidence", f"{m_insight_confidence():.0f}%", "confidence-weighted across signals")
    with c7: metric_card("Signal Coverage", f"{m_review_coverage():.1f}%", f"{N} of {TOTAL_REVIEWS:,} reviews scanned")
    with c8: metric_card("Theme Saturation", m_theme_saturation(), "distinct categories surfaced")

    ai_insight_card(
        summary="Discovery Barriers are driven by trust erosion, not customer habit — the platform's biggest lever for cross-category growth is reducing perceived risk, not increasing exposure to new categories.",
        confidence="High", evidence_n=N, sources="Google Play, Reddit, YouTube, App Store",
        reasoning="Trust/quality signals (55.6%) outweigh price (21.2%) and habit (3.7%) combined more than 2x over. Repeat-buying is shown to be risk-avoidance behavior, not routine.",
        validation="Every signal is quote-grounded against the original review; a sample was manually re-read to confirm tagging accuracy.",
        pm_implication="Roadmap investment should prioritize trust-building surfaces over generic discovery feeds.",
        business_impact="Directly targets the stated Growth objective — increasing % of MAU purchasing a new category monthly.",
        recommended_action="Open Growth Intelligence and Opportunity Workspace for the ranked, evidence-backed opportunity list.")

# =========================================================
# DISCOVERY PIPELINE
# =========================================================
elif page == "Discovery Pipeline":
    st.markdown('<div class="pagetitle">Discovery Pipeline</div>', unsafe_allow_html=True)
    st.markdown('<div class="pagesub">How customer feedback becomes a validated growth signal.</div>', unsafe_allow_html=True)

    st.markdown("""<div class="stepflow">
    <div class="stepbox">Business goal</div><span class="steparrow">→</span>
    <div class="stepbox">Collect feedback</div><span class="steparrow">→</span>
    <div class="stepbox">AI analysis</div><span class="steparrow">→</span>
    <div class="stepbox">Behavior understanding</div><span class="steparrow">→</span>
    <div class="stepbox">Evidence</div><span class="steparrow">→</span>
    <div class="stepbox">Validation</div><span class="steparrow">→</span>
    <div class="stepbox">Insights</div><span class="steparrow">→</span>
    <div class="stepbox">Growth opportunities</div>
    </div>""", unsafe_allow_html=True)

    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.markdown("**Business goal**")
    st.write("Increase the percentage of Monthly Active Customers who purchase from at least one new category every month.")
    st.markdown("**Collect customer feedback**")
    src = {"Google Play": 662, "Reddit": 360, "YouTube comments": 144, "App Store": 10}
    st.markdown(bar_list(src, {k: "#4F5FBF" for k in src}, unit="records"), unsafe_allow_html=True)
    st.markdown("**AI analysis**")
    st.write("Off-topic content (labor/picker posts, industry debate) and bare statements with no reasoning are filtered before extraction. A single controlled Gemini prompt then tags each remaining review with a signal gate followed by structured extraction: repeat-buying signal, category, barrier, reason type, actionable trust-building ask, customer segment, a grounding quote, and confidence.")
    st.markdown('</div>', unsafe_allow_html=True)

# =========================================================
# BEHAVIOR INTELLIGENCE
# =========================================================
elif page == "Behavior Intelligence":
    st.markdown('<div class="pagetitle">Behavior Intelligence</div>', unsafe_allow_html=True)
    st.markdown('<div class="pagesub">Discovery signals behind repeat-category shopping behaviour.</div>', unsafe_allow_html=True)

    counts = df["reason_type"].value_counts().to_dict()
    ai_insight_card(
        summary=f"Trust/quality risk drives {counts.get('trust',0)} of {N} discovery signals — by far the strongest barrier to cross-category exploration.",
        confidence="High", evidence_n=N, sources="Google Play, Reddit, YouTube, App Store",
        reasoning="Customers describe being burned by fake, expired, or damaged products in unfamiliar categories, then retreating to categories they already trust.",
        validation="100% quote-grounded; 20% of signals flagged as possible duplicate/viral content to avoid inflated counts.",
        pm_implication="Habit-breaking mechanics (badges, nudges, discovery feeds) will underperform relative to trust-building features.",
        business_impact="Fixing the dominant barrier has outsized leverage on the % of MAU exploring new categories.",
        recommended_action="Prioritize authenticity guarantees and tamper-evident packaging for electronics and perishables.",
        chart_html=bar_list(counts, REASON_COLORS))

    seg_counts = df["user_segment"].value_counts().to_dict()
    ai_insight_card(
        summary="Heavy, loyal customers show the clearest readiness to explore once trust is addressed — they are the highest-leverage segment for a first experiment.",
        confidence="Medium", evidence_n=N, sources="Google Play, Reddit, YouTube, App Store",
        reasoning="Segment is inferred from review language — frequency cues, price-comparison behavior, and tenure mentions — not verified account data.",
        validation="Segment classification is a text-proxy hypothesis; recommend validating against real behavioral/transactional data before large-scale rollout.",
        pm_implication="quality_focused and price_sensitive customers are distinct populations needing different fixes, not one generic offer.",
        business_impact="Targeting heavy_user first maximizes early conversion probability on the core growth metric.",
        recommended_action="Pilot the Category Trust Badge experiment with heavy_user customers before wider release.",
        chart_html=bar_list(seg_counts, SEGMENT_COLORS, unit="records"))

    cat_counts = df[df["category_mentioned"]!="none"]["category_mentioned"].value_counts().head(8).to_dict()
    ai_insight_card(
        summary="Electronics and perishables (dairy, eggs, produce) concentrate the highest share of trust-risk mentions across categories.",
        confidence="Medium", evidence_n=len(df[df["category_mentioned"]!="none"]), sources="Google Play, Reddit, YouTube, App Store",
        reasoning="High-value and perishable items carry the greatest downside if quality fails, making customers most risk-averse there.",
        validation="Category is extracted only when explicitly named — reviews with no named category are excluded from this view.",
        pm_implication="A platform-wide trust fix is unnecessary; targeted category-level intervention is more efficient.",
        business_impact="Pilot categories represent the fastest path to a measurable lift in cross-category purchase rate.",
        recommended_action="Launch the trust-badge pilot on electronics and dairy/eggs before extending platform-wide.",
        chart_html=bar_list(cat_counts, {k: RED for k in cat_counts}))

# =========================================================
# GROWTH INTELLIGENCE
# =========================================================
elif page == "Growth Intelligence":
    st.markdown('<div class="pagetitle">Growth Intelligence</div>', unsafe_allow_html=True)
    st.markdown('<div class="pagesub">All 8 required discovery questions, answered as validated growth signals.</div>', unsafe_allow_html=True)

    qa = [
        ("Why do customers repeatedly purchase from the same categories?",
         "Not habit-driven (only 3.7% of signal). Customers retreat to categories where they haven't been burned — repeat-buying is risk-avoidance, not routine.", "High"),
        ("What prevents customers from exploring new categories?",
         "Trust/quality risk (55.6%) — fake products, expired/damaged perishables, tampered electronics. Secondary: price uncertainty (21.2%), limited/unavailable SKUs (4.8%).", "High"),
        ("How do customers discover products today?",
         "Weakly — evidence of broken search, unawareness of existing features, and customers leaving for competitors over unavailable specific variants or niche stock.", "Medium"),
        ("What role do habits play in shopping behaviour?",
         "Minimal (3.7%, weakest signal). Price-driven multi-app switching (21.2%) shows active deal-seeking, not loyal habit.", "High"),
        ("What information do customers need before trying a new category?",
         f"{m_exploration_intent():.0f}% of signals named something concrete: authenticity/seller verification, tamper-evident packaging, expiry visibility, working return/replace flow, real-time stock accuracy.", "High"),
        ("What frustrations emerge repeatedly?",
         "Fake/counterfeit goods, expired perishables, broken refund/replacement promises, forced substitutions without consent, unhonored promo codes.", "High"),
        ("Which customer segments are more likely to experiment?",
         "heavy_user — loyal, high-frequency customers most likely to try new categories once trust is addressed.", "Medium"),
        ("What unmet needs emerge consistently?",
         "Authenticity guarantees, transparent real-time pricing, reliable return/replace flows, niche/regional stock visibility, simpler UI for accessibility.", "Medium"),
    ]
    for i, (q, a, conf) in enumerate(qa, 1):
        conf_colors = {"High": (GREEN, GREEN_BG), "Medium": ("#8A6A0F", YELLOW_BG)}
        cc, cbg = conf_colors[conf]
        st.markdown(f"""<div class="card"><div class="ai-kicker"><span class="ai-badge">Signal {i}</span>
        <span class="conf-badge" style="background:{cbg};color:{cc}">CONFIDENCE: {conf.upper()}</span></div>
        <div class="ai-summary" style="font-size:14.5px">{q}</div>
        <div class="section-txt">{a}</div></div>""", unsafe_allow_html=True)

# =========================================================
# EVIDENCE EXPLORER
# =========================================================
elif page == "Evidence Explorer":
    st.markdown('<div class="pagetitle">Evidence Explorer</div>', unsafe_allow_html=True)
    st.markdown('<div class="pagesub">Drill from signal to theme to source review — full traceability.</div>', unsafe_allow_html=True)

    c1, c2, c3 = st.columns(3)
    with c1: theme = st.selectbox("Reason type", ["All"] + sorted(df["reason_type"].unique().tolist()))
    with c2: seg = st.selectbox("Segment", ["All"] + sorted(df["user_segment"].unique().tolist()))
    with c3: conf = st.selectbox("Confidence", ["All", "high", "med", "low"])

    fdf = df.copy()
    if theme != "All": fdf = fdf[fdf["reason_type"]==theme]
    if seg != "All": fdf = fdf[fdf["user_segment"]==seg]
    if conf != "All": fdf = fdf[fdf["confidence"]==conf]

    st.caption(f"{len(fdf)} supporting reviews match this path")
    for _, row in fdf.head(25).iterrows():
        cmap = {"high": GREEN, "med": "#B8860B", "low": MUTED}
        c = cmap.get(row["confidence"], MUTED)
        st.markdown(f"""<div class="evrow"><span style="color:{c};font-weight:700">{row['confidence'].upper()}</span> ·
        <b>{row['reason_type']}</b> · {row['category_mentioned']} · {row['user_segment']}
        <br><i>Row #{row['row_number']}</i> — barrier: {row['barrier_to_new_category']}</div>""", unsafe_allow_html=True)
    with st.expander(f"View all {len(fdf)} matching rows as a table"):
        st.dataframe(fdf, use_container_width=True)

# =========================================================
# OPPORTUNITY WORKSPACE
# =========================================================
elif page == "Opportunity Workspace":
    st.markdown('<div class="pagetitle">Opportunity Workspace</div>', unsafe_allow_html=True)
    st.markdown('<div class="pagesub">Growth experiments ranked by business impact, confidence, and effort.</div>', unsafe_allow_html=True)

    opportunities = [
        ("Category Trust Badge", "Trust/quality risk affecting new-category purchase decisions",
         "105 of 189 signals (55.6%)", "quality_focused, heavy_user", "High", "High", "Medium",
         "Show authenticity/seller-verification signals on category pages with historically high risk mentions.",
         "Increases new-category conversion in electronics/perishables by reducing perceived risk at decision point."),
        ("First-New-Category Return Guarantee", "Customers need explicit reassurance before trying an unfamiliar category",
         f"{m_exploration_intent():.0f}% of signals gave an actionable ask", "heavy_user", "High", "High", "Low",
         "Lightweight 'first try in this category, free return if unsatisfied' prompt targeting the segment with highest readiness.",
         "Directly lifts % of MAU purchasing a new category — targets the segment closest to converting."),
        ("Transparent Real-Time Pricing", "Cross-app price comparison drives switching, not category avoidance directly",
         "40 of 189 signals (21.2%)", "price_sensitive", "Medium", "Medium", "Medium",
         "Show live price vs. MRP and recent-order price consistency at checkout.",
         "Reduces churn to competitor apps; secondary effect on category trust."),
        ("Niche & Regional Stock Visibility", "Customers abandon category exploration silently when stock is inaccurate",
         "9 of 189 signals (4.8%)", "unclear segment", "Low", "Medium", "Low",
         "Surface accurate regional/niche stock status before checkout.",
         "Small volume but low-cost fix; prevents silent category abandonment."),
    ]
    impact_color = {"High": GREEN, "Medium": "#B8860B", "Low": MUTED}
    for title, problem, evidence, segment, impact, conf_lvl, effort, rec, kpi in opportunities:
        st.markdown(f"""<div class="opp-card">
        <div class="ai-summary" style="font-size:15.5px">{title}</div>
        <span class="badge" style="background:{impact_color[impact]}20;color:{impact_color[impact]}">IMPACT: {impact.upper()}</span>
        <span class="badge" style="background:{GREY_BG};color:{INK}">CONFIDENCE: {conf_lvl.upper()}</span>
        <span class="badge" style="background:{GREY_BG};color:{INK}">EFFORT: {effort.upper()}</span>
        <p style="margin-top:10px;font-size:13px;"><b>Problem:</b> {problem}</p>
        <p style="font-size:13px;"><b>Evidence:</b> {evidence} · <b>Affected segment:</b> {segment}</p>
        <p style="font-size:13px;"><b>PM recommendation:</b> {rec}</p>
        <p style="font-size:13px;"><b>Expected KPI impact:</b> {kpi}</p>
        </div>""", unsafe_allow_html=True)

# =========================================================
# AI VALIDATION
# =========================================================
elif page == "AI Validation":
    st.markdown('<div class="pagetitle">AI Validation</div>', unsafe_allow_html=True)
    st.markdown('<div class="pagesub">Why these signals can be trusted — and where they can\'t.</div>', unsafe_allow_html=True)

    c1,c2,c3,c4 = st.columns(4)
    with c1: metric_card("Signal Coverage", f"{m_review_coverage():.1f}%", f"{N} of {TOTAL_REVIEWS:,} carried signal")
    with c2: metric_card("Quote-Grounded", "100%", "every signal requires an exact quote")
    with c3: metric_card("Flagged Duplicates", f"{(df['duplicate_flag']=='yes').sum()}", "flagged, not deleted — visible in Evidence Explorer")
    with c4: metric_card("High-Confidence Signals", f"{(df['confidence']=='high').sum()/N*100:.0f}%", "self-reported by model")

    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.markdown("**Hallucination risk & mitigation**")
    st.write("Every extracted reason/barrier requires a verbatim supporting quote — rows without one are excluded. This prevents the model from inventing plausible-sounding but unfounded reasoning. Confidence scores are self-reported by the model and should be read as a signal of certainty, not a guarantee of correctness.")
    st.markdown('</div>', unsafe_allow_html=True)

    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.markdown("**Source bias & known limitations**")
    st.write("""
    - Reddit rows are mostly post titles, not full post bodies (avg. 70 characters, 773/1,176 rows under 60 characters)
    - App Store sample (n=10) is too small for independent conclusions — directional only
    - Google Play reviews skew toward one-word ratings — main driver of the 16% overall signal rate
    - YouTube comments included substantial off-topic industry-economics debate, filtered before extraction
    - Duplicate/near-identical content is flagged (20% of tagged rows) so theme frequencies aren't inflated
    """)
    st.markdown('</div>', unsafe_allow_html=True)

    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.markdown("**Sampling & human review**")
    st.write("A sample of tagged rows was manually re-read against original source text to confirm reason_type and category assignments were accurate rather than merely plausible-sounding. Low-confidence signals remain visible in Evidence Explorer and should be weighted less heavily in decisions.")
    st.markdown('</div>', unsafe_allow_html=True)

# =========================================================
# LIVE ANALYSIS
# =========================================================
elif page == "Live Analysis":
    st.markdown('<div class="pagetitle">Live Analysis</div>', unsafe_allow_html=True)
    st.markdown('<div class="pagesub">Run the exact extraction pipeline used on all 1,176 reviews, live.</div>', unsafe_allow_html=True)

    st.markdown('<div class="card">', unsafe_allow_html=True)
    secret_key = st.secrets.get("GEMINI_API_KEY", "") if hasattr(st, "secrets") else ""
    if secret_key:
        api_key = secret_key
        st.caption("✓ Using configured API key.")
    else:
        api_key = st.text_input("Gemini API key", type="password", help="Get one free at aistudio.google.com/apikey")

    review_input = st.text_area("Paste a review or comment about a quick-commerce app", height=110,
                                 placeholder="e.g. Ordered a PS5 from Blinkit and the controller was tampered with, never buying electronics from here again")

    PROMPT_TEMPLATE = """You will be given a single user review about a quick-commerce grocery delivery app (Blinkit/Zepto/Instamart).

GOAL: Understand why users repeat-buy the same categories and what stops them from exploring new categories.

STEP 1 — FILTER: Decide if the review has real behavioral signal about shopping habits, category choices, discovery, trust, or barriers to trying something new. Generic praise/complaints with no behavioral detail have no real signal.

STEP 2 — If it has real signal, extract and return ONLY this JSON, nothing else, no markdown fences:
{{
  "has_signal": true or false,
  "repeat_buying_signal": "yes" or "no",
  "category_mentioned": "specific category or none",
  "barrier_to_new_category": "specific barrier or none",
  "reason_type": "one of: habit, trust, convenience, price, no_discovery, other",
  "info_needed_to_trust_new_category": "specific info/reassurance that would help, or not stated",
  "user_segment_signal": "one of: heavy_user, price_sensitive, quality_focused, one_time_complainer, light_new_user, senior_citizen, unclear",
  "quote": "exact short quote under 15 words from the review, or none",
  "confidence": "high, medium, or low"
}}

If has_signal is false, still return the JSON with has_signal: false and other fields as "none".

Review: {review}"""

    if st.button("Analyze review"):
        if not api_key:
            st.error("Please enter your Gemini API key.")
        elif not review_input.strip():
            st.error("Please paste a review to analyze.")
        else:
            with st.spinner("Running structured extraction..."):
                try:
                    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent?key={api_key}"
                    prompt = PROMPT_TEMPLATE.format(review=review_input)
                    resp = requests.post(url, json={"contents": [{"parts": [{"text": prompt}]}]}, timeout=30)
                    resp.raise_for_status()
                    text_out = resp.json()["candidates"][0]["content"]["parts"][0]["text"]
                    text_out = re.sub(r"```json|```", "", text_out).strip()
                    parsed = json.loads(text_out)
                    if not parsed.get("has_signal", True):
                        st.warning("No real behavioral signal detected — filtered out by design.")
                    else:
                        color = REASON_COLORS.get(parsed.get("reason_type","other"), MUTED)
                        st.markdown(f"""<div class="action-strip" style="border-left-color:{color}">
                        <b>{parsed.get('reason_type','—')}</b> · {parsed.get('category_mentioned','—')} ·
                        {parsed.get('user_segment_signal','—')} · confidence: {parsed.get('confidence','—')}<br>
                        <i>"{parsed.get('quote','—')}"</i></div>""", unsafe_allow_html=True)
                    with st.expander("Raw JSON output"):
                        st.json(parsed)
                except Exception as e:
                    st.error(f"Error: {e}")
    st.markdown('</div>', unsafe_allow_html=True)

# =========================================================
# SETTINGS
# =========================================================
elif page == "Settings":
    st.markdown('<div class="pagetitle">Settings</div>', unsafe_allow_html=True)
    st.markdown('<div class="pagesub">Platform configuration and data provenance.</div>', unsafe_allow_html=True)
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.write(f"**Dataset:** tagged_reviews.csv — {N} validated signals from {TOTAL_REVIEWS:,} scanned reviews")
    st.write("**Model:** Gemini 2.0 Flash (structured extraction)")
    st.write("**Live Analysis API key:** configure `GEMINI_API_KEY` under app Secrets to avoid requiring reviewers to supply their own key.")
    st.markdown('</div>', unsafe_allow_html=True)
