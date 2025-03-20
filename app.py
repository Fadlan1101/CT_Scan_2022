import pandas as pd  # pip install pandas openpyxl
import plotly.express as px  # pip install plotly-express
import streamlit as st  # pip install streamlit

# Set Streamlit Page Config
st.set_page_config(
    page_title="CT Scan 2022",
    page_icon="📊",
    layout="wide"
)

# ---- MAIN PAGE ----
st.title("PATIENT CT SCAN IN EMERGENCY DEPARTMENT 2022")
st.markdown("##")  # Adds spacing below the title

# ---- FILE UPLOAD ----
st.sidebar.header("Upload File")
uploaded_file = st.sidebar.file_uploader("Upload an Excel file", type=["xlsx"])

def get_data_from_uploaded_file(uploaded_file):
    try:
        df = pd.read_excel(
            uploaded_file,
            engine='openpyxl',
            sheet_name='Working_Sheet',
            usecols='A:AI',
            nrows=80000,
        )
        return df
    except Exception as e:
        st.error(f"Error loading data: {e}")
        return None

if uploaded_file is not None:
    df = get_data_from_uploaded_file(uploaded_file)
    
    if df is not None:
        # ---- SIDEBAR FILTERS ----
        st.sidebar.header("Search & Filter")

        search_name = st.sidebar.text_input("Search by Name", "")
        gender_filter = st.sidebar.multiselect("Select Gender:", options=sorted(df["Gender"].dropna().unique()), default=sorted(df["Gender"].dropna().unique()))
        age_group_filter = st.sidebar.multiselect("Select Age Group:", options=sorted(df["Age Group"].dropna().unique()), default=sorted(df["Age Group"].dropna().unique()))
        admit_month = st.sidebar.multiselect("Select Admit Month:", options=sorted(df["Month"].dropna().astype(int).unique()), default=sorted(df["Month"].dropna().astype(int).unique()))

        # ---- APPLY FILTERS ----
        filtered_df = df.copy()
        if search_name:
            filtered_df = filtered_df[filtered_df["NAME"].astype(str).str.contains(search_name, case=False, na=False)]
        if gender_filter:
            filtered_df = filtered_df[filtered_df["Gender"].isin(gender_filter)]
        if age_group_filter:
            filtered_df = filtered_df[filtered_df["Age Group"].isin(age_group_filter)]
        if admit_month:
            filtered_df = filtered_df[filtered_df["Month"].isin(admit_month)]

        # ---- DISPLAY FILTERED DATA ----
        st.markdown("### Patient Data")
        st.dataframe(filtered_df)

        # ---- DISPLAY COUNT 'CTscanProsedure' ----
        if "CTscanProsedure" in filtered_df.columns:
            total_CTscanProsedure = int(filtered_df["CTscanProsedure"].count())
            st.subheader(f"Total Patient Perform CT Scan: {total_CTscanProsedure:,}")
        else:
            st.warning("Column 'CTscanProsedure' not found in the dataset!")

        # ---- DISPLAY TOTAL 'bil_ctscan' ----
        if "bil_ctscan" in filtered_df.columns:
            total_bil_ctscan = int(filtered_df["bil_ctscan"].sum())
            st.subheader(f"Total CT Scan Perform: {total_bil_ctscan:,}")
        else:
            st.warning("Column 'bil_ctscan' not found in the dataset!")

        # ---- COUNT 'CTx' VALUES INTO A SINGLE COLUMN ----
        st.markdown("### Count of CT Scan Types")
        ctx_columns = ["CTx1", "CTx2", "CTx3", "CTx4", "CTx5", "CTx6", "CTx7", "CTx8"]
        existing_columns = [col for col in ctx_columns if col in df.columns]

        if existing_columns:
            melted_df = df.melt(value_vars=existing_columns, var_name="CT_Scan_Type", value_name="CT_Scan_Value").dropna()
            ctx_counts = melted_df["CT_Scan_Value"].value_counts().reset_index()
            ctx_counts.columns = ["CT Scan Type", "Count"]
            st.dataframe(ctx_counts)

            fig_ctx = px.bar(ctx_counts, x="CT Scan Type", y="Count", title="Frequency of CT Scan Types", text="Count", color="CT Scan Type")
            st.plotly_chart(fig_ctx, use_container_width=True)
        else:
            st.warning("No CTx columns found in the dataset.")

        # ---- BAR CHART FOR 'bil_ctscan' COLUMN ----
        st.markdown("### Distribution of Patient Perform CT Scan on Visit")
        if "bil_ctscan" in filtered_df.columns:
            bil_ctscan_counts = filtered_df["bil_ctscan"].value_counts().reset_index()
            bil_ctscan_counts.columns = ["bil_ctscan", "Count"]
            bil_ctscan_counts = bil_ctscan_counts.sort_values(by="bil_ctscan")
            st.dataframe(bil_ctscan_counts)

            fig_bil_ctscan = px.bar(bil_ctscan_counts, x="bil_ctscan", y="Count", title="Frequency Distribution of Patient Perform CT Scan on Visit", text="Count", color="bil_ctscan")
            st.plotly_chart(fig_bil_ctscan, use_container_width=True)
        else:
            st.warning("Column 'bil_ctscan' not found in the dataset!")

        # ---- BAR CHART FOR "admitward" (Only where "kodsebabkeluar" = "ADMIT") ----
        st.markdown("### Ward Placement for Admitted Patients")

        if "kodsebabkeluar" in filtered_df.columns and "admitward" in filtered_df.columns:
            admitward_df = filtered_df[filtered_df["kodsebabkeluar"] == "ADMIT"]

            if not admitward_df.empty:
                admitward_counts = admitward_df["admitward"].value_counts().reset_index()
                admitward_counts.columns = ["admitward", "Count"]

                fig_admitward = px.bar(
                    admitward_counts,
                    x="admitward",
                    y="Count",
                    title="Ward Placement for Admitted Patients",
                    text="Count",
                    color="admitward",
                    color_discrete_sequence=px.colors.qualitative.Set3  
                )
                st.plotly_chart(fig_admitward, use_container_width=True)
            else:
                st.warning("No data found for 'admitward' where 'kodsebabkeluar' = 'ADMIT'.")
        else:
            st.warning("Column 'admitward' not found in the dataset!")

        # ---- BAR CHART FOR "PDx" (Only where "kodsebabkeluar" = "ADMIT", Top 3) ----
        st.markdown("### Top 3 Most Common Primary Diagnoses for Ordering CT Scans (Admitted Patients)")

        if "kodsebabkeluar" in filtered_df.columns and "PDx" in filtered_df.columns:
            pdx_df = filtered_df[filtered_df["kodsebabkeluar"] == "ADMIT"]

            if not pdx_df.empty:
                pdx_counts = pdx_df["PDx"].value_counts().reset_index()
                pdx_counts.columns = ["PDx", "Count"]
                pdx_counts = pdx_counts.head(3)  # Show only Top 3

                fig_pdx = px.bar(
                    pdx_counts,
                    x="PDx",
                    y="Count",
                    title="Top 3 Most Common Primary Diagnoses for Ordering CT Scans (Admitted Patients)",
                    text="Count",
                    color="PDx",
                    color_discrete_sequence=px.colors.qualitative.Set3  
                )
                st.plotly_chart(fig_pdx, use_container_width=True)
            else:
                st.warning("No data found for 'PDx' where 'kodsebabkeluar' = 'ADMIT'.")
        else:
            st.warning("Column 'PDx' not found in the dataset!")

        # ---- BAR CHART FOR "PDx" (Only where "kodsebabkeluar" = "HOME", Top 3) ----
        st.markdown("### Top 3 Most Common Primary Diagnoses for Ordering CT Scans (Discharge Patients)")

        if "kodsebabkeluar" in filtered_df.columns and "PDx" in filtered_df.columns:
            pdx_home_df = filtered_df[filtered_df["kodsebabkeluar"] == "HOME"]

            if not pdx_home_df.empty:
                pdx_home_counts = pdx_home_df["PDx"].value_counts().reset_index()
                pdx_home_counts.columns = ["PDx", "Count"]
                pdx_home_counts = pdx_home_counts.head(3)  # Show only Top 3

                fig_pdx_home = px.bar(
                    pdx_home_counts,
                    x="PDx",
                    y="Count",
                    title="Top 3 Most Common Primary Diagnoses for Ordering CT Scans (Discharge Patients)",
                    text="Count",
                    color="PDx",
                    color_discrete_sequence=px.colors.qualitative.Set3  
                )
                st.plotly_chart(fig_pdx_home, use_container_width=True)
            else:
                st.warning("No data found for 'PDx' where 'kodsebabkeluar' = 'HOME'.")

        # ---- HIDE STREAMLIT STYLE ----
        hide_st_style = """
                    <style>
                    #MainMenu {visibility: hidden;}
                    footer {visibility: hidden;}
                    header {visibility: hidden;}
                    </style>
                    """
        st.markdown(hide_st_style, unsafe_allow_html=True)
else:
    st.warning("Please upload an Excel file to proceed.")
