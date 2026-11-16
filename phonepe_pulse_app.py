from pathlib import Path
import base64
import pandas as pd
import numpy as np
import plotly.express as px
import streamlit as st

# ============================================================
# PHONEPE PULSE ANALYTICS — CONSOLIDATED NAVIGATION VERSION
# Sidebar: Overview | Aggregated Data | Map Data | Top Data | Data Quality
# ============================================================

st.set_page_config(
    page_title="PhonePe Pulse Analytics",
    page_icon="📱",
    layout="wide",
    initial_sidebar_state="expanded",
)

PROJECT_ROOT = Path(
    r"C:\Users\HP\OneDrive\Documents\fita project\pulse-main\pulse-main"
)
DATA = PROJECT_ROOT / "data"
BACKGROUND_IMAGE = Path(
    r"C:\Users\HP\OneDrive\Documents\fita project\Pastel Phone Payment Shopping Scene.png"
)

FILES = {
    "Aggregated Transaction": DATA / "aggregated/transaction/country/india/transaction_analysis_2018_2026/phonepe_india_master_2018_2026.csv",
    "Aggregated Merchant India": DATA / "aggregated/merchant/country/india/merchant_analysis_2018_2026/merchant_india_master_2018_2026.csv",
    "Aggregated Merchant State": DATA / "aggregated/merchant/country/india/merchant_state_analysis_2018_2026/merchant_state_master_2018_2026.csv",
    "Aggregated User India": DATA / "aggregated/user/country/india/user_india_analysis_2018_2026/user_india_master_2018_2026.csv",
    "Aggregated User State": DATA / "aggregated/user/country/india/user_state_analysis_2018_2026/user_state_master_2018_2026.csv",
    "Map State": DATA / "map/map_analysis_2018_2026/map_state_master_all_categories_2018_2026.csv",
    "Map District": DATA / "map/map_analysis_2018_2026/map_district_master_all_categories_2018_2026.csv",
    "Top Master": DATA / "top/top_analysis_2018_2026/top_master_all_2018_2026.csv",
    "Validation": DATA / "aggregated/transaction/country/india/transaction_analysis_2018_2026/aggregated_vs_map_transaction_validation.csv",
    "Top Missing Files": DATA / "top/top_analysis_2018_2026/top_missing_json_files.csv",
}

@st.cache_data(show_spinner=False)
def read_csv(path_string: str) -> pd.DataFrame:
    path = Path(path_string)
    if not path.is_file():
        return pd.DataFrame()
    try:
        return pd.read_csv(path, low_memory=False)
    except Exception:
        return pd.DataFrame()

@st.cache_data(show_spinner=False)
def read_background_b64(path_string: str):
    path = Path(path_string)
    if not path.is_file():
        return None
    try:
        return base64.b64encode(path.read_bytes()).decode("ascii")
    except Exception:
        return None

def load(name: str) -> pd.DataFrame:
    frame = read_csv(str(FILES[name])).copy()
    if frame.empty:
        return frame
    for col in ["Year", "QuarterNumber", "Transactions", "Amount", "RegisteredCount", "MetricValue"]:
        if col in frame.columns:
            frame[col] = pd.to_numeric(frame[col], errors="coerce")
    for col in ["Category", "Scope", "Level", "Quarter", "State", "StateFolder", "District", "EntityName", "MetricName"]:
        if col in frame.columns:
            frame[col] = frame[col].astype("string").str.strip()
    if "Category" in frame.columns:
        frame["Category"] = frame["Category"].astype(str).str.title()
    if "Scope" in frame.columns:
        frame["Scope"] = frame["Scope"].astype(str).str.title()
    if "Level" in frame.columns:
        frame["Level"] = frame["Level"].astype(str).str.title()
    return frame

def fmt(value):
    if value is None or pd.isna(value):
        return "Not available"
    value = float(value)
    if abs(value) >= 1_000_000_000_000:
        return f"{value / 1_000_000_000_000:,.2f}T"
    if abs(value) >= 1_000_000_000:
        return f"{value / 1_000_000_000:,.2f}B"
    if abs(value) >= 1_000_000:
        return f"{value / 1_000_000:,.2f}M"
    if abs(value) >= 100_000:
        return f"{value / 100_000:,.2f}L"
    return f"{value:,.0f}"

def pct_fmt(value):
    if value is None or pd.isna(value):
        return "N/A"
    return f"{value:+.2f}%"

def chart_style(fig, height=None):
    fig.update_layout(
        template="plotly_dark",
        paper_bgcolor="rgba(10,15,35,0)",
        plot_bgcolor="rgba(14,22,48,0.45)",
        font=dict(color="#E7E9FF", family="Arial"),
        margin=dict(l=18, r=24, t=60, b=30),
        legend_title_text="",
        title_font=dict(size=17, color="#F4F0FF"),
        hoverlabel=dict(bgcolor="#171638", font_color="#FFFFFF"),
    )
    fig.update_xaxes(gridcolor="rgba(148,163,255,0.14)", zerolinecolor="rgba(148,163,255,0.18)")
    fig.update_yaxes(gridcolor="rgba(148,163,255,0.14)", zerolinecolor="rgba(148,163,255,0.18)")
    if height:
        fig.update_layout(height=height)
    return fig

def periodize(frame):
    frame = frame.copy()
    frame["Year"] = pd.to_numeric(frame["Year"], errors="coerce")
    frame["QuarterNumber"] = pd.to_numeric(frame["QuarterNumber"], errors="coerce")
    frame = frame.dropna(subset=["Year", "QuarterNumber"])
    frame["Year"] = frame["Year"].astype(int)
    frame["QuarterNumber"] = frame["QuarterNumber"].astype(int)
    frame["Period"] = frame["Year"].astype(str) + " Q" + frame["QuarterNumber"].astype(str)
    return frame

def hero_banner():
    encoded = read_background_b64(str(BACKGROUND_IMAGE))
    image_css = ""
    if encoded:
        image_css = f"background-image: linear-gradient(90deg, rgba(255,255,255,.80) 0%, rgba(255,255,255,.57) 48%, rgba(255,255,255,.10) 100%), url('data:image/png;base64,{encoded}'); background-size: cover; background-position: center right;"
    else:
        image_css = "background-image: radial-gradient(ellipse at 88% 15%,rgba(217,70,239,.18),transparent 28%),linear-gradient(120deg,#F4F2FF,#E7F1FF,#FFF0F7);"
    st.markdown(f"""
    <div class="phonepe-hero" style="{image_css}">
      <div class="hero-kicker">✦ &nbsp; PULSE ANALYTICS STUDIO</div>
      <div class="hero-title">PhonePe <span>Pulse</span></div>
      <div class="hero-subtitle">A clearer view of transactions, merchants and users across India.</div>
      <div class="hero-tags"><span>AGGREGATED DATA</span><span>MAP INTELLIGENCE</span><span>TOP RANKINGS</span></div>
    </div>
    """, unsafe_allow_html=True)

def latest_period(frame):
    if frame.empty or not {"Year", "QuarterNumber"}.issubset(frame.columns):
        return None, None
    periods = frame[["Year", "QuarterNumber"]].dropna()
    if periods.empty:
        return None, None
    year = int(periods["Year"].max())
    quarter = int(periods.loc[periods["Year"] == year, "QuarterNumber"].max())
    return year, quarter

def category_metric(category):
    return "Transactions" if category == "Transaction" else "RegisteredCount"

# ----------------------- DESIGN -----------------------
st.markdown("""
<style>
[data-testid="stAppViewContainer"] {
    background: radial-gradient(ellipse at 8% 0%,rgba(124,58,237,.10),transparent 30%),linear-gradient(145deg,#F7F8FF,#F4F2FF 55%,#FFF7FC);
    color:#172554;
}
[data-testid="stHeader"] {background:rgba(247,248,255,.86);}
.block-container {max-width:1550px;padding-top:1.2rem;padding-bottom:3rem;}
[data-testid="stSidebar"] {background:linear-gradient(180deg,#0C1230,#171238 72%,#21113A);border-right:1px solid rgba(139,92,246,.32);}
[data-testid="stSidebar"] * {color:#F1EEFF;}
[data-testid="stSidebar"] h1 {font-size:1.35rem!important;color:#fff!important;}
h1 {color:#172554!important;font-weight:850!important;letter-spacing:-.04em;}
h2,h3 {color:#27245B!important;letter-spacing:-.02em;}
p, label {color:#334155;}
[data-testid="stMetric"] {background:linear-gradient(135deg,#FFFFFF,#F3EEFF);border:1px solid rgba(139,92,246,.36);border-radius:18px;padding:17px;min-height:112px;box-shadow:0 7px 22px rgba(66,46,130,.08);}
[data-testid="stMetricLabel"] p {color:#4C4771!important;font-weight:650!important;font-size:.85rem!important;}
[data-testid="stMetricValue"] {color:#251653!important;font-weight:850!important;font-size:clamp(1.15rem,1.9vw,1.8rem)!important;overflow-wrap:anywhere;}
[data-testid="stPlotlyChart"] {background:linear-gradient(140deg,rgba(255,255,255,.92),rgba(244,241,255,.9));border:1px solid rgba(139,92,246,.2);border-radius:19px;padding:7px;box-shadow:0 7px 24px rgba(70,45,130,.06);}
[data-testid="stDataFrame"] {border:1px solid rgba(139,92,246,.25);border-radius:13px;overflow:hidden;}
[data-testid="stSelectbox"] [data-baseweb="select"]>div,[data-testid="stMultiSelect"] [data-baseweb="select"]>div {background:#FFFFFF;border:1px solid #DDD6FE;border-radius:10px;}
.stButton>button {background:linear-gradient(105deg,#6D28D9,#9333EA,#C026D3);color:white;border:0;border-radius:10px;font-weight:700;}
.phonepe-hero {position:relative;overflow:hidden;min-height:225px;padding:27px 29px;margin:0 0 23px;border-radius:24px;border:1px solid rgba(139,92,246,.28);box-shadow:0 12px 36px rgba(54,40,110,.11);background-repeat:no-repeat!important;}
.hero-kicker {color:#5B21B6;font-weight:850;letter-spacing:.12em;font-size:.73rem;}
.hero-title {margin-top:13px;color:#172554;font-size:clamp(2rem,4vw,3.2rem);line-height:1.05;font-weight:900;letter-spacing:-.05em;}
.hero-title span {background:linear-gradient(90deg,#6D28D9,#9333EA,#BE185D);-webkit-background-clip:text;-webkit-text-fill-color:transparent;}
.hero-subtitle {color:#1E293B;max-width:650px;line-height:1.6;margin-top:11px;font-size:1rem;}
.hero-tags {display:flex;gap:8px;flex-wrap:wrap;margin-top:15px;}
.hero-tags span {border:1px solid rgba(109,40,217,.25);background:rgba(255,255,255,.82);color:#4C1D95;border-radius:999px;padding:7px 11px;font-size:.67rem;letter-spacing:.04em;font-weight:800;}
.feature-card {padding:16px;min-height:104px;border-radius:16px;background:linear-gradient(135deg,#fff,#F2EEFF);border:1px solid rgba(139,92,246,.24);box-shadow:0 5px 16px rgba(70,45,130,.05);}
.feature-title {color:#312E81;font-weight:800;font-size:.9rem;}
.feature-desc {color:#475569;font-size:.77rem;line-height:1.45;margin-top:6px;}
.section-kicker {color:#7C3AED;font-size:.72rem;font-weight:850;letter-spacing:.14em;}
@media(max-width:700px){.phonepe-hero{padding:19px;}.hero-title{font-size:2rem;}}
</style>
""", unsafe_allow_html=True)

# ----------------------- NAVIGATION -----------------------
st.sidebar.markdown("""
<div style="display:flex;align-items:center;gap:10px;padding:5px 0 12px">
 <div style="width:44px;height:44px;border-radius:50%;display:flex;align-items:center;justify-content:center;background:linear-gradient(135deg,#7C3AED,#4F46E5,#BE185D);color:white;font-size:25px;font-weight:900;box-shadow:0 0 22px #5524b855">₹</div>
 <div><div style="font-size:18px;font-weight:850;color:white">PhonePe Pulse</div><div style="font-size:12px;color:#C4B5FD">Analytics Studio</div></div>
</div>
""", unsafe_allow_html=True)

page = st.sidebar.radio(
    "MAIN MENU",
    ["Overview", "Aggregated Data", "Map Data", "Top Data", "Data Quality"],
)
st.sidebar.divider()
st.sidebar.caption("DATA COVERAGE")
st.sidebar.caption("2018–2026 · available source periods")
st.sidebar.caption("2026 data available through Q2 in this dataset.")

# ----------------------- OVERVIEW -----------------------
if page == "Overview":
    hero_banner()
    st.markdown('<div class="section-kicker">INDIA-WIDE SNAPSHOT</div>', unsafe_allow_html=True)
    map_state = load("Map State")
    if map_state.empty:
        st.error("Map State master CSV was not found or could not be read.")
    else:
        year, quarter = latest_period(map_state)
        latest = map_state[(map_state["Year"] == year) & (map_state["QuarterNumber"] == quarter)]
        tx = latest[latest["Category"] == "Transaction"]
        merchants = latest[latest["Category"] == "Merchant"]
        users = latest[latest["Category"] == "User"]
        c1, c2, c3, c4 = st.columns(4)
        c1.metric(f"Total Transactions · {year} Q{quarter}", fmt(tx["Transactions"].sum()))
        c2.metric("Transaction Amount", f"₹{tx['Amount'].sum()/1e12:,.2f}T" if "Amount" in tx and tx["Amount"].notna().any() else "Unavailable")
        c3.metric("Registered Merchants", fmt(merchants["RegisteredCount"].sum()))
        c4.metric("Registered Users", fmt(users["RegisteredCount"].sum()))
        st.caption("Merchant and user values are registration snapshots summed across available state records. 2026 is a partial year.")
        left, right = st.columns([1.15, 1])
        with left:
            st.subheader("Transaction Trend by Year")
            tx_all = map_state[map_state["Category"] == "Transaction"]
            annual = tx_all.groupby("Year", as_index=False).agg(Transactions=("Transactions", "sum")).sort_values("Year")
            annual["Year"] = annual["Year"].astype(int).astype(str)
            fig = px.line(annual, x="Year", y="Transactions", markers=True, title="All-state transaction totals")
            fig.update_traces(line=dict(color="#9333EA", width=3), marker=dict(color="#DB2777", size=7))
            st.plotly_chart(chart_style(fig), use_container_width=True)
        with right:
            st.subheader(f"Top 10 States · {year} Q{quarter}")
            top_states = tx.groupby("State", as_index=False).agg(Transactions=("Transactions", "sum")).nlargest(10, "Transactions").sort_values("Transactions")
            fig = px.bar(top_states, x="Transactions", y="State", orientation="h", title="Transaction count by state")
            fig.update_traces(marker_color="#8B5CF6")
            st.plotly_chart(chart_style(fig), use_container_width=True)
        st.subheader("Explore the analytics sections")
        cols = st.columns(4)
        cards = [
            ("Aggregated Data", "Payment category and registration trends"),
            ("Map Data", "State share, growth, district and 3D explorer"),
            ("Top Data", "State and selected district rankings"),
            ("Data Quality", "Validation and source availability"),
        ]
        for col, (title, desc) in zip(cols, cards):
            with col:
                st.markdown(f'<div class="feature-card"><div class="feature-title">✦ {title}</div><div class="feature-desc">{desc}</div></div>', unsafe_allow_html=True)

# ----------------------- AGGREGATED DATA -----------------------
elif page == "Aggregated Data":
    st.title("Aggregated Data")
    st.write("Category-level transaction and registration trends.")
    subcategory = st.radio("DATA CATEGORY", ["Transaction", "Merchant", "User"], horizontal=True)

    if subcategory == "Transaction":
        df = load("Aggregated Transaction")
        dataset_label = "Aggregated Transaction — P2P, Retail and Utility"
    elif subcategory == "Merchant":
        scope = st.radio("Merchant view", ["India trend", "State comparison"], horizontal=True)
        df = load("Aggregated Merchant India" if scope == "India trend" else "Aggregated Merchant State")
        dataset_label = f"Aggregated Merchant — {scope}"
    else:
        scope = st.radio("User view", ["India trend", "State comparison"], horizontal=True)
        df = load("Aggregated User India" if scope == "India trend" else "Aggregated User State")
        dataset_label = f"Aggregated User — {scope}"

    if df.empty:
        st.error(f"{dataset_label}: master CSV not found or unreadable.")
    else:
        st.success(f"{dataset_label} · {len(df):,} rows loaded")
        view = df.copy()
        if "State" in view.columns and view["State"].notna().any():
            states = sorted(view["State"].dropna().astype(str).unique().tolist())
            state_choice = st.selectbox("State", ["All States"] + states)
            if state_choice != "All States":
                view = view[view["State"].astype(str) == state_choice]
        if "Category" in view.columns:
            cats = sorted(view["Category"].dropna().astype(str).unique().tolist())
            category_choice = st.selectbox("Payment category", ["All categories"] + cats)
            if category_choice != "All categories":
                view = view[view["Category"].astype(str) == category_choice]
        metric_options = [m for m in ["Transactions", "RegisteredCount", "registeredCount", "Amount"] if m in view.columns and pd.to_numeric(view[m], errors="coerce").notna().any()]
        if not metric_options:
            st.warning("No available numeric metric in this dataset.")
        else:
            default_metric = "Transactions" if "Transactions" in metric_options else metric_options[0]
            metric = st.selectbox("Metric", metric_options, index=metric_options.index(default_metric))
            if "Year" in view.columns:
                years = sorted(pd.to_numeric(view["Year"], errors="coerce").dropna().astype(int).unique().tolist())
                if years:
                    year_choice = st.selectbox("Year filter", ["All Years"] + years, index=0)
                    if year_choice != "All Years":
                        view = view[view["Year"] == year_choice]
            view[metric] = pd.to_numeric(view[metric], errors="coerce")
            if "Year" in view.columns and "QuarterNumber" in view.columns and view[metric].notna().any():
                trend = periodize(view.dropna(subset=[metric]))
                group_cols = ["Year", "QuarterNumber", "Period"]
                if "Category" in trend.columns and category_choice if "Category" in view.columns else False:
                    group_cols.append("Category")
                trend = trend.groupby(group_cols, as_index=False).agg(Value=(metric, "sum")).sort_values(["Year", "QuarterNumber"])
                fig = px.line(trend, x="Period", y="Value", color="Category" if "Category" in group_cols else None, markers=True, title=f"{metric} trend")
                st.plotly_chart(chart_style(fig), use_container_width=True)
            elif metric in ["Amount"]:
                st.info("Amount is unavailable in the Aggregated Transaction source JSON; blank values are not zero.")
        st.subheader("Data preview")
        st.dataframe(view.head(500), use_container_width=True, hide_index=True)

# ----------------------- MAP DATA -----------------------
elif page == "Map Data":
    st.title("Map Data")
    st.write("State contribution, quarterly growth, district rankings and interactive 3D exploration.")
    category = st.radio("DATA CATEGORY", ["Transaction", "Merchant", "User"], horizontal=True)
    view_mode = st.selectbox("Analysis view", ["State Trends & Percentages", "District Rankings", "3D Explorer"])
    state_df = load("Map State")
    district_df = load("Map District")

    metric = st.selectbox("Metric", ["Transactions", "Amount"] if category == "Transaction" else ["RegisteredCount"], key="map_metric")

    if view_mode == "State Trends & Percentages":
        if state_df.empty:
            st.error("Map State master is unavailable.")
        else:
            allcat = state_df[state_df["Category"] == category].copy()
            state_periods = periodize(allcat)
            if state_periods.empty:
                st.warning("No state records available.")
            else:
                state_periods[metric] = pd.to_numeric(state_periods[metric], errors="coerce")
                state_periods = state_periods.dropna(subset=[metric])
                if metric == "RegisteredCount":
                    state_periods = state_periods.sort_values(["StateFolder", "Year", "QuarterNumber"])
                    # registration data is a point-in-time snapshot, not a flow to accumulate
                    state_periods = state_periods.drop_duplicates(["StateFolder", "Year", "QuarterNumber"], keep="last")
                sums = state_periods.groupby(["Year", "QuarterNumber"], as_index=False).agg(PeriodTotal=(metric, "sum"))
                state_periods = state_periods.merge(sums, on=["Year", "QuarterNumber"], how="left")
                state_periods["SharePct"] = np.where(state_periods["PeriodTotal"] != 0, state_periods[metric] / state_periods["PeriodTotal"] * 100, np.nan)
                state_periods["GrowthPct"] = state_periods.groupby("StateFolder")[metric].pct_change(fill_method=None) * 100

                states = sorted(state_periods["State"].dropna().astype(str).unique().tolist())
                state_view = st.radio("Trend selection", ["India total", "Compare states", "Single state"], horizontal=True)
                year_options = sorted(state_periods["Year"].astype(int).unique().tolist())
                default_states = []
                latest_y, latest_q = latest_period(state_periods)
                latest_values = state_periods[(state_periods["Year"] == latest_y) & (state_periods["QuarterNumber"] == latest_q)]
                default_states = latest_values.nlargest(min(6, len(latest_values)), metric)["State"].tolist()

                if state_view == "Compare states":
                    selected_states = st.multiselect("Choose states", states, default=default_states)
                    selected_state_periods = state_periods[state_periods["State"].isin(selected_states)]
                elif state_view == "Single state":
                    one_state = st.selectbox("Choose state", states)
                    selected_state_periods = state_periods[state_periods["State"] == one_state]
                else:
                    selected_state_periods = state_periods.groupby(["Year", "QuarterNumber", "Period"], as_index=False).agg(Value=(metric, "sum"))
                    selected_state_periods["SharePct"] = 100.0
                    selected_state_periods["GrowthPct"] = selected_state_periods["Value"].pct_change(fill_method=None) * 100
                    selected_state_periods["State"] = "India total"

                if state_view != "India total":
                    selected_state_periods = selected_state_periods.copy()
                    selected_state_periods["Value"] = selected_state_periods[metric]

                if not selected_state_periods.empty:
                    trend = selected_state_periods.copy()
                    fig = px.line(
                        trend, x="Period", y="Value", color="State", markers=True,
                        hover_data={"SharePct": ":.2f", "GrowthPct": ":.2f", "Value": ":,.0f"},
                        title=f"{category} · {metric} with share and quarter growth",
                    )
                    fig.update_traces(line=dict(width=2.8))
                    st.plotly_chart(chart_style(fig), use_container_width=True)

                selected_year = st.selectbox("Ranking year", year_options, index=len(year_options)-1)
                quarter_options = sorted(state_periods.loc[state_periods["Year"] == selected_year, "QuarterNumber"].astype(int).unique().tolist())
                selected_quarter = st.selectbox("Ranking quarter", quarter_options, index=len(quarter_options)-1)
                ranking = state_periods[(state_periods["Year"] == selected_year) & (state_periods["QuarterNumber"] == selected_quarter)].copy()
                ranking = ranking.sort_values(metric, ascending=False)
                ranking["Rank"] = range(1, len(ranking)+1)
                ranking["Share %"] = ranking["SharePct"]
                ranking["Growth %"] = ranking["GrowthPct"]
                ranking["Previous Quarter Value"] = ranking[metric] / (1 + ranking["GrowthPct"] / 100)
                ranking.loc[~np.isfinite(ranking["Previous Quarter Value"]), "Previous Quarter Value"] = np.nan
                st.subheader(f"State Share & Growth · {selected_year} Q{selected_quarter}")
                top_rank = ranking.head(12).sort_values(metric)
                fig = px.bar(top_rank, x=metric, y="State", orientation="h", text=top_rank["Share %"].map(lambda v: f"{v:.1f}%" if pd.notna(v) else "N/A"), hover_data={"Share %": ":.2f", "Growth %": ":.2f"}, title="Top states · bar labels show share of available state total")
                fig.update_traces(marker_color="#8B5CF6", textposition="outside", cliponaxis=False)
                fig.update_layout(margin=dict(r=70))
                st.plotly_chart(chart_style(fig), use_container_width=True)
                display_cols = ["Rank", "State", metric, "Share %", "Growth %"]
                st.dataframe(ranking[display_cols], use_container_width=True, hide_index=True, column_config={"Share %": st.column_config.NumberColumn(format="%.2f%%"), "Growth %": st.column_config.NumberColumn(format="%.2f%%")})
                st.caption("Share is each state's portion of the sum of available state values in that period. Growth compares the same state with the previous calendar quarter. Registration counts are snapshots, not quarterly activity flows.")

    elif view_mode == "District Rankings":
        if district_df.empty:
            st.error("Map District master is unavailable.")
        else:
            d = district_df[district_df["Category"] == category].copy()
            d = periodize(d)
            states = sorted(d["State"].dropna().astype(str).unique().tolist())
            state_choice = st.selectbox("District geography", ["All India"] + states)
            if state_choice != "All India":
                d = d[d["State"] == state_choice]
            years = sorted(d["Year"].unique().tolist())
            year_choice = st.selectbox("Year", years, index=len(years)-1)
            d = d[d["Year"] == year_choice]
            quarters = sorted(d["QuarterNumber"].unique().tolist())
            quarter_choice = st.selectbox("Quarter", quarters, index=len(quarters)-1)
            d = d[d["QuarterNumber"] == quarter_choice].copy()
            d[metric] = pd.to_numeric(d[metric], errors="coerce")
            ranking = d.dropna(subset=[metric]).sort_values(metric, ascending=False).head(15).copy()
            if not ranking.empty:
                ranking["District label"] = ranking["District"].astype(str) + " · " + ranking["State"].astype(str)
                ranking["Share %"] = ranking[metric] / d[metric].sum() * 100 if d[metric].sum() else np.nan
                fig = px.bar(ranking.sort_values(metric), x=metric, y="District label", orientation="h", text=ranking["Share %"].map(lambda v: f"{v:.1f}%" if pd.notna(v) else "N/A"), title=f"Top districts · {category} · {year_choice} Q{quarter_choice}")
                fig.update_traces(marker_color="#C026D3", textposition="outside", cliponaxis=False)
                fig.update_layout(margin=dict(r=60))
                st.plotly_chart(chart_style(fig), use_container_width=True)
                st.dataframe(ranking[["State", "District", metric, "Share %"]], use_container_width=True, hide_index=True)
            else:
                st.info("No records for this selection.")

    else:  # 3D Explorer is nested under Map Data, not a separate main menu page
        if state_df.empty:
            st.error("Map State master is unavailable.")
        else:
            d3 = periodize(state_df[state_df["Category"] == category].copy())
            d3[metric] = pd.to_numeric(d3[metric], errors="coerce")
            state_names = sorted(d3["State"].dropna().astype(str).unique().tolist())
            y_options = sorted(d3["Year"].unique().tolist())
            default_years = y_options[-3:] if len(y_options) > 3 else y_options
            chosen_states = st.multiselect("Select states for 3D comparison", state_names, default=state_names[:6])
            chosen_years = st.multiselect("Select years", y_options, default=default_years)
            if not chosen_states or not chosen_years:
                st.info("Choose at least one state and one year.")
            else:
                d3 = d3[d3["State"].isin(chosen_states) & d3["Year"].isin(chosen_years)]
                d3 = d3.dropna(subset=[metric])
                plot3 = d3[["State", "Year", "QuarterNumber", "Period", metric]].copy()
                if not plot3.empty:
                    fig = px.scatter_3d(plot3, x="Year", y="QuarterNumber", z=metric, color="State", hover_name="State", hover_data={"Period": True, metric: ":,.0f"}, title=f"3D Explorer · {category} · {metric}")
                    fig.update_traces(marker=dict(size=5, opacity=.88, line=dict(width=.4, color="#E9D5FF")))
                    fig.update_layout(template="plotly_dark", paper_bgcolor="#10102C", plot_bgcolor="#10102C", font_color="#EEE7FF", height=650, scene=dict(xaxis_title="Year", yaxis_title="Quarter", zaxis_title=metric, bgcolor="#10102C"), margin=dict(l=0, r=0, t=60, b=0))
                    st.plotly_chart(fig, use_container_width=True)
                    st.dataframe(plot3.sort_values(["Year", "QuarterNumber", "State"]), use_container_width=True, hide_index=True)
                st.caption("This is an interactive historical chart. The source dataset is not a live transaction feed.")

# ----------------------- TOP DATA -----------------------
elif page == "Top Data":
    st.title("Top Data")
    st.write("Rank states, India-wide selected districts, or top districts within a state.")
    category = st.radio("DATA CATEGORY", ["Transaction", "Merchant", "User"], horizontal=True)
    level_choice = st.selectbox("Ranking view", ["Top States", "Top Districts Across India", "Districts Within a State"])
    top = load("Top Master")
    scope, level = (("Country", "State") if level_choice == "Top States" else ("Country", "District") if level_choice == "Top Districts Across India" else ("State", "District"))
    if top.empty:
        st.error("Top master CSV is unavailable.")
    else:
        view = top[(top["Category"] == category) & (top["Scope"] == scope) & (top["Level"] == level)].copy()
        if view.empty:
            st.warning("No source records for this ranking selection.")
        else:
            if level_choice == "Districts Within a State":
                state_names = sorted(view["State"].dropna().astype(str).unique().tolist())
                state_choice = st.selectbox("Choose state", state_names)
                view = view[view["State"].astype(str) == state_choice]
            years = sorted(view["Year"].dropna().astype(int).unique().tolist())
            year = st.selectbox("Year", years, index=len(years)-1)
            view = view[view["Year"] == year]
            quarters = sorted(view["QuarterNumber"].dropna().astype(int).unique().tolist())
            quarter = st.selectbox("Quarter", quarters, index=len(quarters)-1)
            view = view[view["QuarterNumber"] == quarter].copy()
            view["MetricValue"] = pd.to_numeric(view["MetricValue"], errors="coerce")
            ranking = view.dropna(subset=["MetricValue"]).sort_values("MetricValue", ascending=False).drop_duplicates(subset=["EntityName", "StateFolder"]).head(15).copy()
            if not ranking.empty:
                if level_choice == "Top Districts Across India":
                    ranking["Display"] = ranking["EntityName"].astype(str)
                else:
                    ranking["Display"] = ranking["EntityName"].astype(str)
                ranking["Rank"] = range(1, len(ranking)+1)
                fig = px.bar(ranking.sort_values("MetricValue"), x="MetricValue", y="Display", orientation="h", title=f"Top {category} · {year} Q{quarter}")
                fig.update_traces(marker_color="#8B5CF6")
                st.plotly_chart(chart_style(fig), use_container_width=True)
                show_cols = [c for c in ["Rank", "Category", "State", "EntityName", "Year", "Quarter", "MetricName", "MetricValue"] if c in ranking.columns]
                st.dataframe(ranking[show_cols], use_container_width=True, hide_index=True)
            st.caption("Top dataset contains selected entities from the source; it is not a complete census of every district.")

# ----------------------- DATA QUALITY -----------------------
elif page == "Data Quality":
    st.title("Data Quality")
    st.write("Dataset availability, transaction validation and source gaps.")
    rows = []
    for name, path in FILES.items():
        exists = path.is_file()
        frame = load(name) if exists else pd.DataFrame()
        rows.append({"Dataset": name, "Status": "Found" if exists else "Not found", "Rows": len(frame) if exists else None})
    st.subheader("Master file status")
    st.dataframe(pd.DataFrame(rows), use_container_width=True, hide_index=True)

    validation = load("Validation")
    st.subheader("Aggregated vs Map Transaction validation")
    if not validation.empty and "Status" in validation.columns:
        matches = int((validation["Status"] == "Match").sum())
        mismatches = int((validation["Status"] == "Mismatch").sum())
        missing_comparisons = int((validation["Status"] == "Missing from one dataset").sum()) if (validation["Status"] == "Missing from one dataset").any() else 0
        c1, c2, c3 = st.columns(3)
        c1.metric("Matching records", f"{matches:,}")
        c2.metric("Mismatches", f"{mismatches:,}")
        c3.metric("Missing comparisons", f"{missing_comparisons:,}")
    else:
        st.warning("Transaction validation report is missing or empty.")

    missing = load("Top Missing Files")
    st.subheader("Top dataset source gaps")
    if not missing.empty:
        st.metric("Reported missing JSON files", f"{len(missing):,}")
        if {"Category", "Scope"}.issubset(missing.columns):
            summary = missing.groupby(["Category", "Scope"], as_index=False).size().rename(columns={"size": "Missing files"})
            st.dataframe(summary, use_container_width=True, hide_index=True)
        with st.expander("View missing file details"):
            st.dataframe(missing, use_container_width=True, hide_index=True)
    else:
        st.success("No missing-file records are listed in the report.")

    st.info("Aggregated Transaction source JSON does not provide an Amount field. Unavailable amount values are not treated as zero.")

st.sidebar.divider()
st.sidebar.caption("PhonePe Pulse · Analytics Project")
st.sidebar.caption("Historical dataset dashboard — not live PhonePe data.")
