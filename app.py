import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px

# 1. Page Configuration
st.set_page_config(page_title="OptiLogix | Supply Chain Analytics", layout="wide")

st.title("🚚 OptiLogix: Freight & Logistics Performance Dashboard")
st.markdown("Operational analytics tracking fulfillment efficiency, carrier SLA compliance, and route bottlenecks.")

# 2. Generate Synthetic Logistics Data
@st.cache_data
def load_data():
    np.random.seed(42)
    n_records = 1200
    carriers = ['BlueDart Express', 'Delhivery Hub', 'DHL Supply', 'FedEx Ground', 'Shadowfax']
    hubs = ['Mumbai Central', 'Delhi NCR', 'Bengaluru South', 'Kolkata East', 'Chennai North']
    statuses = ['Delivered', 'In Transit', 'Delayed', 'Returned']
    
    data = {
        'Shipment_ID': [f"SHP-{10000 + i}" for i in range(n_records)],
        'Carrier': np.random.choice(carriers, n_records, p=[0.25, 0.25, 0.2, 0.15, 0.15]),
        'Origin_Hub': np.random.choice(hubs, n_records),
        'Destination_Hub': np.random.choice(hubs, n_records),
        'Freight_Cost_INR': np.random.uniform(1200, 8500, n_records).round(2),
        'Transit_Time_Days': np.random.exponential(scale=2.8, size=n_records).round(1) + 1,
        'Expected_Lead_Time': np.random.choice([2, 3, 4, 5], n_records),
        'Status': np.random.choice(statuses, n_records, p=[0.72, 0.14, 0.10, 0.04])
    }
    df = pd.DataFrame(data)
    df['SLA_Breached'] = df['Transit_Time_Days'] > df['Expected_Lead_Time']
    return df

df = load_data()

# 3. Sidebar Filters
st.sidebar.header("Filter Telemetry")
selected_carrier = st.sidebar.multiselect("Select Carrier", options=df['Carrier'].unique(), default=df['Carrier'].unique())
selected_origin = st.sidebar.selectbox("Origin Hub", options=['All Hubs'] + list(df['Origin_Hub'].unique()))

filtered_df = df[df['Carrier'].isin(selected_carrier)]
if selected_origin != 'All Hubs':
    filtered_df = filtered_df[filtered_df['Origin_Hub'] == selected_origin]

# 4. Top KPI Metric Cards
total_shipments = len(filtered_df)
ontime_rate = ((filtered_df['Status'] == 'Delivered') & (~filtered_df['SLA_Breached'])).sum() / (total_shipments or 1) * 100
avg_freight = filtered_df['Freight_Cost_INR'].mean()
sla_breaches = filtered_df['SLA_Breached'].sum()

col1, col2, col3, col4 = st.columns(4)
col1.metric("Total Shipments", f"{total_shipments:,}")
col2.metric("On-Time In-Full (OTIF)", f"{ontime_rate:.1f}%")
col3.metric("Avg Freight Cost", f"₹{avg_freight:,.0f}")
col4.metric("SLA Breaches", f"{sla_breaches}", delta=f"-{sla_breaches / (total_shipments or 1) * 100:.1f}%", delta_color="inverse")

st.markdown("---")

# 5. Visual Analytics
row1_col1, row1_col2 = st.columns(2)

with row1_col1:
    st.subheader("Carrier Lead-Time vs. Target SLA")
    carrier_perf = filtered_df.groupby('Carrier')[['Transit_Time_Days', 'Expected_Lead_Time']].mean().reset_index()
    fig1 = px.bar(carrier_perf, x='Carrier', y=['Transit_Time_Days', 'Expected_Lead_Time'],
                  barmode='group', labels={'value': 'Days', 'variable': 'Metric'})
    st.plotly_chart(fig1, use_container_width=True)

with row1_col2:
    st.subheader("Fulfillment Status Distribution")
    status_counts = filtered_df['Status'].value_counts().reset_index()
    status_counts.columns = ['Status', 'Count']
    fig2 = px.pie(status_counts, names='Status', values='Count', hole=0.45)
    st.plotly_chart(fig2, use_container_width=True)

# 6. Detailed Tabular View
st.subheader("High-Risk Shipments (SLA Breached)")
breached_df = filtered_df[filtered_df['SLA_Breached']][['Shipment_ID', 'Carrier', 'Origin_Hub', 'Destination_Hub', 'Transit_Time_Days', 'Expected_Lead_Time', 'Freight_Cost_INR']]
st.dataframe(breached_df.head(10), use_container_width=True)
