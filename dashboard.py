import streamlit as st
import pandas as pd
import io
from datetime import datetime

# Configure the Streamlit app's overall layout and UI appearance settings.
# This includes the page title in the browser tab, favicon, layout width, and sidebar visibility.
st.set_page_config(
    page_title="CSV Data Dashboard",
    page_icon="",
    layout="wide",  # Wide layout allows more horizontal space for charts and tables.
    initial_sidebar_state="expanded"  # Sidebar is expanded by default when the app loads.
)

# Injecting custom CSS styling directly into the app using HTML for better control over aesthetics.
# This adds custom styles for headers, cards, filter panels, and table formatting.
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        font-weight: 700;
        color: #1f2937;
        margin-bottom: 1rem;
        text-align: center;
    }
    .sub-header {
        font-size: 1.2rem;
        color: #6b7280;
        text-align: center;
        margin-bottom: 2rem;
    }
    .metric-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 1rem;
        border-radius: 10px;
        color: white;
        text-align: center;
        margin: 0.5rem 0;
    }
    .filter-section {
        background-color: #f8fafc;
        padding: 1.5rem;
        border-radius: 10px;
        border: 1px solid #e2e8f0;
        margin: 1rem 0;
    }
    .sort-section {
        background-color: #fef7f0;
        padding: 1.5rem;
        border-radius: 10px;
        border: 1px solid #fed7aa;
        margin: 1rem 0;
    }
    .stDataFrame {
        border: 1px solid #e2e8f0;
        border-radius: 10px;
    }
</style>
""", unsafe_allow_html=True)

# Initialize session state to store the uploaded DataFrame and the filtered DataFrame across user interactions.
# This allows data to persist between reruns caused by UI changes or filters.
if 'df' not in st.session_state:
    st.session_state.df = None  # Original DataFrame from uploaded CSV
if 'filtered_df' not in st.session_state:
    st.session_state.filtered_df = None  # DataFrame after applying filters and sorting

# List of required column names that the uploaded CSV must contain.
# Used during validation to ensure compatibility with the dashboard.
REQUIRED_COLUMNS = [
    'number', 'sys_created_on', 'incident_state', 'short_description',
    'u_internal_incident', 'priority', 'u_sfdc_case_number', 'category',
    'assignment_group', 'assigned_to', 'company'
]

# List of column names that the user can sort and filter on in the UI.
# Only these fields are exposed to user interactions.
SORTABLE_FIELDS = [
    'u_internal_incident',
    'priority', 
    'category',
    'assignment_group',
    'assigned_to',
    'company'
]

# Function to validate that the uploaded CSV contains all required columns.
# Returns a boolean indicating validity, and a list of missing columns if any.
def validate_csv(df):
    missing_columns = [col for col in REQUIRED_COLUMNS if col not in df.columns]
    return len(missing_columns) == 0, missing_columns

# Function to apply user-selected filters to the DataFrame.
# Filters are passed as a dictionary mapping column names to selected values.
def apply_filters(df, filters):
    filtered_df = df.copy()
    for field, values in filters.items():
        if values and len(values) > 0:
            # Retain only rows where the field value is in selected values
            filtered_df = filtered_df[filtered_df[field].isin(values)]
    return filtered_df

# Function to apply multi-level sorting based on user selection.
# Each sort level contains a field and an ascending/descending flag.
def apply_sorting(df, sort_config):
    if not sort_config:
        return df  # Return as-is if no sorting specified
    sort_columns = []
    sort_ascending = []
    for field_config in sort_config:
        if field_config['field'] != 'None':
            sort_columns.append(field_config['field'])
            sort_ascending.append(field_config['ascending'])
    if sort_columns:
        return df.sort_values(by=sort_columns, ascending=sort_ascending)
    return df

# Function to create a downloadable CSV string buffer.
# Used for generating downloadable CSVs from filtered or original data.
def create_download_link(df, filename):
    csv = df.to_csv(index=False)
    b64 = io.StringIO(csv).getvalue().encode()  # Convert CSV string to bytes
    return b64

# Main application logic — defines the UI and interaction flow.
def main():
    # Display the app title and subtitle at the top using custom styling.
    st.markdown('<h1 class="main-header">CSV Data Dashboard</h1>', unsafe_allow_html=True)
    st.markdown('<p class="sub-header">Upload, sort, filter, and analyze your incident data</p>', unsafe_allow_html=True)
    
    # Sidebar section for uploading a CSV file.
    with st.sidebar:
        st.header("File Upload")
        uploaded_file = st.file_uploader(
            "Choose a CSV file",
            type="csv",
            help="Upload a CSV file with the required columns"
        )
        
        if uploaded_file is not None:
            try:
                df = pd.read_csv(uploaded_file)  # Read uploaded file into DataFrame
                is_valid, missing_cols = validate_csv(df)  # Validate required columns
                
                if is_valid:
                    st.success(f"File uploaded successfully! ({len(df)} rows)")
                    st.session_state.df = df  # Store in session state
                else:
                    st.error(f"Missing required columns: {', '.join(missing_cols)}")
                    st.session_state.df = None
                    
            except Exception as e:
                st.error(f"Error reading file: {str(e)}")
                st.session_state.df = None
    
    # Main content area only displays if a valid file has been uploaded
    if st.session_state.df is not None:
        df = st.session_state.df
        
        # Display four key metrics in horizontally aligned cards
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.markdown(f"""
            <div class="metric-card">
                <h3>{len(df)}</h3>
                <p>Total Records</p>
            </div>
            """, unsafe_allow_html=True)
        
        with col2:
            unique_companies = df['company'].nunique()
            st.markdown(f"""
            <div class="metric-card">
                <h3>{unique_companies}</h3>
                <p>Companies</p>
            </div>
            """, unsafe_allow_html=True)
        
        with col3:
            unique_categories = df['category'].nunique()
            st.markdown(f"""
            <div class="metric-card">
                <h3>{unique_categories}</h3>
                <p>Categories</p>
            </div>
            """, unsafe_allow_html=True)
        
        with col4:
            unique_groups = df['assignment_group'].nunique()
            st.markdown(f"""
            <div class="metric-card">
                <h3>{unique_groups}</h3>
                <p>Assignment Groups</p>
            </div>
            """, unsafe_allow_html=True)
        
        # Divide screen into two columns for sorting and filtering UI
        col_sort, col_filter = st.columns([1, 1])
        
        # Custom sorting section that allows up to 6 levels of field sorting
        with col_sort:
            st.markdown('<div class="sort-section">', unsafe_allow_html=True)
            st.subheader("Custom Sorting")
            st.write("Define your custom sort order (drag priority: 1=highest, 6=lowest)")
            sort_config = []
            for i in range(6):
                col_field, col_order = st.columns([3, 1])
                with col_field:
                    field = st.selectbox(
                        f"Sort Level {i+1}",
                        ['None'] + SORTABLE_FIELDS,
                        key=f"sort_field_{i}",
                        help=f"Select field for sort priority {i+1}"
                    )
                with col_order:
                    ascending = st.selectbox(
                        "Order",
                        [True, False],
                        format_func=lambda x: "↑ Asc" if x else "↓ Desc",
                        key=f"sort_order_{i}"
                    )
                sort_config.append({'field': field, 'ascending': ascending})
            st.markdown('</div>', unsafe_allow_html=True)
        
        # Filtering section lets the user filter on dropdown values of allowed columns
        with col_filter:
            st.markdown('<div class="filter-section">', unsafe_allow_html=True)
            st.subheader("Data Filters")
            st.write("Filter data by selecting values from dropdowns")
            filters = {}
            for field in SORTABLE_FIELDS:
                unique_values = sorted(df[field].dropna().unique().tolist())
                selected_values = st.multiselect(
                    f"Filter by {field.replace('_', ' ').title()}",
                    unique_values,
                    key=f"filter_{field}",
                    help=f"Select one or more {field.replace('_', ' ')} values"
                )
                filters[field] = selected_values
            st.markdown('</div>', unsafe_allow_html=True)
        
        # Apply the filters and sorting to the original dataset and 
        # results are dynamically narrowed based on selection
        filtered_df = apply_filters(df, filters)
        final_df = apply_sorting(filtered_df, sort_config)
        st.session_state.filtered_df = final_df  # Store for export or reuse
        
        # Display summary message showing how many rows are being shown
        st.subheader("Results Summary")
        if len(final_df) != len(df):
            st.info(f"Showing {len(final_df)} of {len(df)} records after filtering")
        else:
            st.info(f"Showing all {len(df)} records")
        
        # Display preview table with pagination controls to show a portion of final_df depending on pagination
        st.subheader("Data Preview")
        col_page1, col_page2, col_page3 = st.columns([1, 2, 1])
        with col_page1:
            page_size = st.selectbox("Rows per page", [10, 25, 50, 100], index=1)
        with col_page3:
            total_pages = (len(final_df) - 1) // page_size + 1 if len(final_df) > 0 else 1
            page_number = st.number_input(
                f"Page (1-{total_pages})", 
                min_value=1, 
                max_value=total_pages, 
                value=1
            )
        start_idx = (page_number - 1) * page_size
        end_idx = start_idx + page_size
        if len(final_df) > 0:
            display_df = final_df.iloc[start_idx:end_idx]
            st.dataframe(
                display_df,
                use_container_width=True,
                height=400
            )
            
            # For download options for both filtered and original data
            st.subheader("Export Data")
            col_download1, col_download2 = st.columns(2)
            with col_download1:
                csv_data = create_download_link(final_df, "filtered_data.csv")
                st.download_button(
                    label="Download Filtered Data",
                    data=final_df.to_csv(index=False),
                    file_name=f"filtered_data_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                    mime="text/csv",
                    help="Download the current filtered and sorted dataset"
                )
            with col_download2:
                st.download_button(
                    label="Download Original Data",
                    data=df.to_csv(index=False),
                    file_name=f"original_data_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                    mime="text/csv",
                    help="Download the original uploaded dataset"
                )
        else:
            st.warning("No data matches the current filters.")
        
        # For generating charts inorder to visualize filtered data for quick insights
        if len(final_df) > 0:
            st.subheader("Quick Insights")
            insight_col1, insight_col2 = st.columns(2)
            with insight_col1:
                st.write("**Top 5 Companies by Incident Count:**")
                company_counts = final_df['company'].value_counts().head()
                st.bar_chart(company_counts)
            with insight_col2:
                st.write("**Priority Distribution:**")
                priority_counts = final_df['priority'].value_counts()
                st.bar_chart(priority_counts)
    
    else:
        # When no file is uploaded, instructions on how to begin using the app.
        st.markdown("""
        ### To get started:
        1. Upload a CSV file using the sidebar
        2. Your file must contain these exact columns:
            - `number`, `sys_created_on`, `incident_state`, `short_description`
            - `u_internal_incident`, `priority`, `u_sfdc_case_number`, `category`
            - `assignment_group`, `assigned_to`, `company`
        3. Use the sorting controls to define custom sort order
        4. Apply filters to focus on specific data
        5. View and analyze your data in real-time
        6. Export your filtered results
        """)

if __name__ == "__main__":
    main()
