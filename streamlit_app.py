import streamlit as st
import pandas as pd
import requests
from datetime import datetime
import json
import os
import base64

# --- Login credentials JSON ---
CREDENTIALS_PATH = "credentials.json"
DEFAULT_CREDENTIALS = {
    "users": [
        {"username": "asif", "password": "asif123"}
    ]
}

def load_credentials():
    # Always reload credentials and ensure file exists with correct content
    if not os.path.exists(CREDENTIALS_PATH):
        with open(CREDENTIALS_PATH, "w") as f:
            json.dump(DEFAULT_CREDENTIALS, f)
    with open(CREDENTIALS_PATH, "r") as f:
        return json.load(f)["users"]

def check_login(username, password, users):
    # Ensure both username and password are stripped of whitespace and compared as strings
    for user in users:
        if str(user["username"]).strip() == str(username).strip() and str(user["password"]) == str(password):
            return True
    return False

def login_page():
    # Read image and encode as base64 for inline HTML
    try:
        with open("aaabed.jpg", "rb") as img_file:
            img_bytes = img_file.read()
            img_base64 = base64.b64encode(img_bytes).decode()
        img_html = f'<img src="data:image/jpeg;base64,{img_base64}" style="height:100px; margin-bottom: 30px;" />'
    except Exception:
        img_html = ""
    st.markdown(
        f"""
        <div style="display: flex; flex-direction: column; align-items: center; margin-top: 60px;">
            {img_html}
            <h2>AAABED Dashboards Login Portal</h2>
        </div>
        """,
        unsafe_allow_html=True
    )
    st.write("")
    username = st.text_input("Username", key="login_username")
    password = st.text_input("Password", type="password", key="login_password")
    login_btn = st.button("Login")
    return username, password, login_btn

# --- Login logic ---
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

if not st.session_state.logged_in:
    users = load_credentials()
    username, password, login_btn = login_page()
    if login_btn:
        if check_login(username, password, users):
            st.session_state.logged_in = True
            st.success("Login successful! Please wait...")
            st.rerun()  # Use st.rerun() instead of st.experimental_rerun()
        else:
            st.error("Invalid username or password.")
    st.stop()

# Page config
st.set_page_config(layout="wide", page_title="Warehouse Stock Dashboard")

# Custom CSS for metrics, header, and table styling
st.markdown("""
<style>
.metric-card {
    background-color: #1E2A3A;
    padding: 18px 10px 10px 18px;
    border-radius: 8px;
    margin-bottom: 10px;
}
.metric-label {
    color: #FFFFFF;
    font-size: 16px;
}
.metric-value {
    color: #4DD0E1;
    font-size: 28px;
    font-weight: bold;
}
.dashboard-header {
    padding: 0px 0px 20px 0px;
}
.dashboard-title {
    font-size: 32px;
    font-weight: bold;
    color: #262730;
}
.datetime {
    font-size: 14px;
    color: #666;
}
th, td {
    border: 1px solid #A0D1FF !important;
}
th {
    background-color: #118DFF !important;
    color: white !important;
    border: 1px solid #A0D1FF !important;
}
/* Alternate row backgrounds */
tbody tr:nth-child(odd) td {
    background-color: #D7ECFE !important;
}
tbody tr:nth-child(even) td {
    background-color: #FFFFFF !important;
}
/* Total row (last row) */
tbody tr:last-child td {
    background-color: #E3F5FA !important;
    font-weight: bold;
}
/* Example: change first row of table body (not header) */
tbody tr:first-child td {
    background-color: orange !important;
}
</style>
""", unsafe_allow_html=True)

# Show logo above filter section (sidebar)
logo_path = "aaabed.jpg"
with st.sidebar:
    st.image(logo_path, use_container_width=True)  # Updated parameter name
    st.markdown("<br>", unsafe_allow_html=True)  # Add some space after logo

# Add dashboard header with refresh button on the right
header_col1, header_col2 = st.columns([8, 1])
with header_col1:
    st.markdown(f"""
    <div class="dashboard-header">
        <div class="dashboard-title">Stock Dashboard (MB52)</div>
        <div class="datetime">As of: {datetime.now().strftime("%d %B %Y, %I:%M %p")}</div>
    </div>
    """, unsafe_allow_html=True)
with header_col2:
    if st.session_state.get("logged_in", False):
        if st.button("🔄 Refresh Data", help="Reload all data from the API/database"):
            st.cache_data.clear()
            st.rerun()

@st.cache_data(ttl=120)
def fetch_data():
    response = requests.get("http://localhost:8000/api/stock")
    if response.status_code == 200:
        return pd.DataFrame(response.json())
    else:
        return pd.DataFrame()

data = None
refresh = False

data = fetch_data()

if data.empty:
    st.error("No data available. Make sure the FastAPI backend is running and returning data.")
else:
    # Filters
    st.sidebar.header("Filters")
    plant = st.sidebar.selectbox("Plant Name", ["All"] + sorted(data['PlantName'].dropna().unique().tolist()))
    material = st.sidebar.selectbox("Material", ["All"] + sorted(data['MaterialNumber'].unique().tolist()))
    material_desc = st.sidebar.selectbox("Material Description", ["All"] + sorted(data['MaterialDescription'].dropna().unique().tolist()))
    batch = st.sidebar.selectbox("Batch Number", ["All"] + sorted(data['BatchNumber'].dropna().unique().tolist()))
    storage = st.sidebar.selectbox(
        "Storage Location",
        ["All"] + sorted(data['StorageLocationDescription'].dropna().unique().tolist())
    )

    filtered = data.copy()
    if plant != "All":
        filtered = filtered[filtered['PlantName'] == plant]
    if material != "All":
        filtered = filtered[filtered['MaterialNumber'] == material]
    if material_desc != "All":
        filtered = filtered[filtered['MaterialDescription'] == material_desc]
    if batch != "All":
        filtered = filtered[filtered['BatchNumber'] == batch]
    if storage != "All":
        filtered = filtered[filtered['StorageLocationDescription'] == storage]

    # Top metrics (dynamic)
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        total_stock = filtered['UnrestrictedStock'].astype(float).sum()
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-label">Total Stock</div>
            <div class="metric-value">{total_stock:,.0f}</div>
        </div>
        """, unsafe_allow_html=True)
    with col2:
        total_stock_value = filtered['StockValue'].astype(float).sum()
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-label">Total Stock Value</div>
            <div class="metric-value">{total_stock_value:,.0f}</div>
        </div>
        """, unsafe_allow_html=True)
    with col3:
        plant_count = filtered['PlantName'].nunique()
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-label">Plant Count</div>
            <div class="metric-value">{plant_count:,d}</div>
        </div>
        """, unsafe_allow_html=True)
    with col4:
        material_count = filtered['MaterialNumber'].nunique()
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-label">Total Materials</div>
            <div class="metric-value">{material_count:,d}</div>
        </div>
        """, unsafe_allow_html=True)

    # Helper to add total row to a DataFrame for int/float columns
    def add_total_row(df):
        if df.empty:
            return df
        
        total_row = {}
        first_text_column = True  # Flag to track first text column
        
        for col in df.columns:
            if pd.api.types.is_numeric_dtype(df[col]):
                total_row[col] = df[col].astype(float).sum()
            else:
                if first_text_column:
                    total_row[col] = "Total"
                    first_text_column = False
                else:
                    total_row[col] = None  # or "" for empty string
        
        return pd.concat([df, pd.DataFrame([total_row])], ignore_index=True)

    # Format UnrestrictedStock and StockValue as string with commas
    def format_commas(df, cols):
        for col in cols:
            if col in df.columns:
                df[col] = df[col].apply(lambda x: f"{int(float(x)):,}" if pd.notnull(x) and x != "Total" else x)
        return df

    # Storage Location Summary
    st.subheader("Storage Location Summary")
    storage_summary = (
        filtered.groupby(['StorageLocationDescription', 'PlantName'], as_index=False)
        .agg({'UnrestrictedStock': 'sum', 'StockValue': 'sum'})
        .sort_values('UnrestrictedStock', ascending=False)
    )
    storage_summary = add_total_row(storage_summary)
    storage_summary = format_commas(storage_summary, ["UnrestrictedStock", "StockValue"])
    st.dataframe(
        storage_summary,
        column_config={
            "StorageLocationDescription": st.column_config.TextColumn("Storage Location"),
            "PlantName": st.column_config.TextColumn("Plant Name"),
            "UnrestrictedStock": st.column_config.TextColumn("Unrestricted Stock"),
            "StockValue": st.column_config.TextColumn("Total Stock Value"),
        },
        hide_index=True,
        use_container_width=True
    )

    # Batch Summary
    st.subheader("Batch Summary")
    batch_summary = (
        filtered.groupby(['BatchNumber', 'PlantName', 'MaterialNumber'], as_index=False)
        .agg({'UnrestrictedStock': 'sum', 'StockInTransfer': 'sum'})
        .sort_values('UnrestrictedStock', ascending=False)
    )
    batch_summary = add_total_row(batch_summary)
    batch_summary = format_commas(batch_summary, ["UnrestrictedStock", "StockInTransfer"])
    st.dataframe(
        batch_summary,
        column_config={
            "BatchNumber": st.column_config.TextColumn("Batch Number"),
            "PlantName": st.column_config.TextColumn("Plant Name"),
            "MaterialNumber": st.column_config.TextColumn("Material No."),
            "UnrestrictedStock": st.column_config.TextColumn("Unrestricted Stock"),
            "StockInTransfer": st.column_config.TextColumn("Stock in Transfer"),
        },
        hide_index=True,
        use_container_width=True
    )

    # Material Wise Summary
    st.subheader("Material Wise Summary")
    material_summary = (
        filtered.groupby(
            ['MaterialType', 'MaterialNumber', 'MaterialDescription']
        ).agg({
            'UnrestrictedStock': 'sum',
            'StockValue': 'sum',
            'StockInTransfer': 'sum',
            'BlockedStock': 'sum'
        }).reset_index()
    ).sort_values('UnrestrictedStock', ascending=False)

    material_summary = add_total_row(material_summary)
    material_summary = format_commas(material_summary, 
        ["UnrestrictedStock", "StockValue", "StockInTransfer", "BlockedStock"])
    
    st.dataframe(
        material_summary,
        column_config={
            "MaterialType": st.column_config.TextColumn("Material Type"),
            "MaterialNumber": st.column_config.TextColumn("Material Number"),
            "MaterialDescription": st.column_config.TextColumn("Description"),
            "UnrestrictedStock": st.column_config.TextColumn("Current Stock"),
            "StockValue": st.column_config.TextColumn("Stock Value"),
            "StockInTransfer": st.column_config.TextColumn("Stock in Transfer"),
            "BlockedStock": st.column_config.TextColumn("Blocked Stock")
        },
        hide_index=True,
        use_container_width=True
    )
