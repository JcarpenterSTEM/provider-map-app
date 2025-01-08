import pandas as pd
import plotly.express as px
import streamlit as st

# Define input file path (if needed locally, remove if uploading through Streamlit)
file_path = r"C:\Users\JordanCarpenter\OneDrive - Specialist Telemed\Documents\Data November 2024\Development\PODs Input.csv"

# Load the CSV data
def load_data(file_path):
    df = pd.read_csv(file_path)
    # Split 'Licenses' into lists for states, assuming 'Licenses' contains comma-separated state abbreviations
    df['Licenses'] = df['Licenses'].apply(lambda x: x.split(',') if pd.notna(x) else [])
    return df

# Function to filter data based on user selection
def filter_data(df, providers=None, specialties=None):
    if providers:
        df = df[df['Provider'].isin(providers)]
    if specialties:
        df = df[df['Specialty'].isin(specialties)]
    return df

# Generate a color map for providers or specialties
def generate_color_map(unique_values):
    colors = px.colors.qualitative.Plotly  # Use Plotly's qualitative color scheme
    color_map = {val: colors[i % len(colors)] for i, val in enumerate(unique_values)}
    return color_map

# Plot US map with enhanced features
def plot_us_map(df):
    # Flatten data for plotting with a list of dictionaries
    rows = []
    for _, row in df.iterrows():
        for state in row['Licenses']:
            rows.append({
                'Provider': row['Provider'],
                'Specialty': row['Specialty'],
                'State': state.strip()  # Clean whitespace
            })
    plot_df = pd.DataFrame(rows)

    # Map state abbreviations to full names for hover info
    state_names = {
        'AL': 'Alabama', 'AK': 'Alaska', 'AZ': 'Arizona', 'AR': 'Arkansas', 'CA': 'California',
        'CO': 'Colorado', 'CT': 'Connecticut', 'DE': 'Delaware', 'FL': 'Florida', 'GA': 'Georgia',
        'HI': 'Hawaii', 'ID': 'Idaho', 'IL': 'Illinois', 'IN': 'Indiana', 'IA': 'Iowa',
        'KS': 'Kansas', 'KY': 'Kentucky', 'LA': 'Louisiana', 'ME': 'Maine', 'MD': 'Maryland',
        'MA': 'Massachusetts', 'MI': 'Michigan', 'MN': 'Minnesota', 'MS': 'Mississippi', 'MO': 'Missouri',
        'MT': 'Montana', 'NE': 'Nebraska', 'NV': 'Nevada', 'NH': 'New Hampshire', 'NJ': 'New Jersey',
        'NM': 'New Mexico', 'NY': 'New York', 'NC': 'North Carolina', 'ND': 'North Dakota', 'OH': 'Ohio',
        'OK': 'Oklahoma', 'OR': 'Oregon', 'PA': 'Pennsylvania', 'RI': 'Rhode Island', 'SC': 'South Carolina',
        'SD': 'South Dakota', 'TN': 'Tennessee', 'TX': 'Texas', 'UT': 'Utah', 'VT': 'Vermont',
        'VA': 'Virginia', 'WA': 'Washington', 'WV': 'West Virginia', 'WI': 'Wisconsin', 'WY': 'Wyoming'
    }
    plot_df['State Name'] = plot_df['State'].map(state_names)

    # Generate a color map for providers
    color_map = generate_color_map(plot_df['Provider'].unique())
    plot_df['Color'] = plot_df['Provider'].map(color_map)

    # Aggregate providers and specialties by state for hover
    plot_df['Selected Details'] = plot_df.apply(
        lambda x: f"<span style='color:{x['Color']}'>{x['Provider']} ({x['Specialty']})</span>", axis=1
    )
    aggregated = plot_df.groupby(['State', 'State Name']).agg({'Selected Details': ' | '.join}).reset_index()

    # Plot map using Plotly
    fig = px.scatter_geo(
        aggregated,
        locations="State",
        locationmode="USA-states",
        hover_name="State Name",
        hover_data={"Selected Details": True, "State": False},
        scope="usa",
        title="Provider Licenses by State",
    )
    fig.update_traces(marker=dict(color="LightBlue", size=10))
    st.plotly_chart(fig)

    # Display details in the sidebar with matching colors
    st.sidebar.title("Provider Details")
    for _, row in aggregated.iterrows():
        st.sidebar.markdown(f"### **{row['State Name']}**", unsafe_allow_html=True)
        providers = row['Selected Details'].split(" | ")
        for provider in providers:
            st.sidebar.markdown(f"{provider}", unsafe_allow_html=True)
        st.sidebar.markdown("---")  # Divider between states

# Main function
def main():
    st.title("Provider License and Specialty Map")

    # Upload CSV file
    uploaded_file = st.file_uploader("Choose a CSV file", type="csv")
    if uploaded_file:
        df = load_data(uploaded_file)

        # Sidebar filters
        provider_list = df['Provider'].unique()
        specialty_list = df['Specialty'].unique()
        
        st.sidebar.header("Filter Providers")
        selected_providers = st.sidebar.multiselect("Select Providers", provider_list)

        st.sidebar.header("Filter by Specialty")
        selected_specialties = st.sidebar.multiselect("Select Specialties", specialty_list)

        # Filter the data
        filtered_df = filter_data(df, providers=selected_providers, specialties=selected_specialties)

        # Display the map with the filtered data
        plot_us_map(filtered_df)

if __name__ == "__main__":
    main()
