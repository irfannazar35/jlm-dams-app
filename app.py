import streamlit as st
import pandas as pd
import plotly.express as px

# 1. Page Configuration
st.set_page_config(
    page_title="Dams in Small Dams Division Jhelum",
    page_icon="🌊",
    layout="wide"
)

# 2. Load and Clean Data
@st.cache_data
def load_data():
    df = pd.read_csv('damsjlm.csv')

    # Clean newline characters from column names
    df.columns = [col.replace('\n', ' ').strip() for col in df.columns]

    # Clean numeric columns
    numeric_cols = [
        'Gross Storage Capacity (Aft)',
        'Live storage (Aft)',
        'C.C.A. (Acres)',
        'Completion Cost (million)',
        'Capacity of Channel (Cfs)',
        'Length of Canal (ft)',
        'Height (ft)'
    ]

    for col in numeric_cols:
        if col in df.columns:
            df[col] = (
                df[col]
                .astype(str)
                .str.replace(",", "", regex=False)
            )
            df[col] = pd.to_numeric(df[col], errors='coerce')

    return df

# Load data
df = load_data()

# 3. Sidebar Navigation & Filters
st.sidebar.title("Search & Filter")
st.sidebar.info("Use the filters below to explore specific regions or dam types.")

districts = st.sidebar.multiselect(
    "Select District",
    options=df['District'].unique(),
    default=df['District'].unique()
)

dam_types = st.sidebar.multiselect(
    "Dam Type",
    options=df['Type of Dam'].unique(),
    default=df['Type of Dam'].unique()
)

# Filter data
filtered_df = df[(df['District'].isin(districts)) & (df['Type of Dam'].isin(dam_types))]

# 4. Main Dashboard UI
st.title("🌊 Regional Dams Infrastructure Dashboard")
st.markdown("---")

# KPI Metrics
m1, m2, m3, m4 = st.columns(4)
with m1:
    st.metric("Total Dams", len(filtered_df))

storage = filtered_df['Gross Storage Capacity (Aft)'].sum()
cca = filtered_df['C.C.A. (Acres)'].sum()
investment = filtered_df['Completion Cost (million)'].sum()

with m2:
    st.metric("Storage Capacity (Aft)", f"{storage:,.0f}")

with m3:
    st.metric("Irrigation Area (Acres)", f"{cca:,.0f}")

with m4:
    st.metric("Total Investment", f"PKR {investment:,.1f}M")

st.markdown("---")

# 5. Interactive Map
st.subheader("📍 Dam Locations")
fig_map = px.scatter_mapbox(
    filtered_df,
    lat="Decimal Latitude",
    lon="Decimal Longitude",
    hover_name="Name of Dam",
    hover_data=["Tehsil", "River / Nullah", "Gross Storage Capacity (Aft)"],
    color="District",
    size="Gross Storage Capacity (Aft)",
    zoom=8,
    height=600,
    color_discrete_sequence=px.colors.qualitative.Bold
)
fig_map.update_layout(mapbox_style="carto-positron")
st.plotly_chart(fig_map, use_container_width=True)

# 6. Technical Analysis
col1, col2 = st.columns(2)

with col1:
    st.subheader("Capacity vs. Cost Analysis")
    fig_scatter = px.scatter(
        filtered_df,
        x="Gross Storage Capacity (Aft)",
        y="Completion Cost (million)",
        color="Type of Dam",
        size="Height (ft)",
        hover_name="Name of Dam",
        template="plotly_white"
    )
    st.plotly_chart(fig_scatter, use_container_width=True)

with col2:
    st.subheader("Operational Status Distribution")
    fig_pie = px.pie(
        filtered_df,
        names="Operational / Non-Operational",
        color_discrete_sequence=["#2ecc71", "#e74c3c"]
    )
    st.plotly_chart(fig_pie, use_container_width=True)

# 7. Data Explorer
with st.expander("🔍 View Complete Details Table"):
    st.dataframe(filtered_df.drop(columns=['Decimal Latitude', 'Decimal Longitude']))

