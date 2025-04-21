import streamlit as st
import pandas as pd
from utils.scrapingdog_api import ScrapingDog

# Configure page
st.set_page_config(page_title="Job Search API", page_icon="🔍", layout="wide")

# ISO 3166 Alpha-2 Country Codes
COUNTRIES = {
    "US": "United States",
    "GB": "United Kingdom",
    "CA": "Canada",
    "AU": "Australia",
    "IN": "India",
    "DE": "Germany",
    "FR": "France",
    "BR": "Brazil",
    "JP": "Japan",
    "SG": "Singapore",
    # Add more countries as needed
}

# Main app
st.title("🔍 Advanced Job Search API")
st.write("Find job listings with powerful search filters.")

# Sidebar for filters
with st.sidebar:
    st.subheader("Basic Filters")
    platform_options = ["LinkedIn", "Indeed", "Glassdoor", "Monster", "ZipRecruiter"]
    
    # Platform selection
    col1, col2 = st.columns([1, 4])
    with col1:
        select_all = st.checkbox("All", value=True)
    with col2:
        selected_platforms = st.multiselect(
            "Platform(s)", 
            platform_options,
            default=platform_options if select_all else [],
            disabled=select_all,
            label_visibility="collapsed"
        )
    
    count = st.slider("Number of results", 1, 50, 10)
    days_ago = st.slider("Posted within last (days)", 1, 30, 7)
    
    # Advanced filters
    st.markdown("---")
    st.subheader("Advanced Filters")
    
    # Country dropdown
    country = st.selectbox(
        "Country",
        options=list(COUNTRIES.keys()),
        format_func=lambda x: f"{x} - {COUNTRIES[x]}",
        index=0
    )
    
    # Remote/radius options
    remote_only = st.checkbox("Remote jobs only")
    search_radius = st.slider("Search radius (miles)", 0, 100, 10, disabled=remote_only)
    
    # Job type chips
    job_type = st.selectbox(
        "Job Type",
        ["Any", "Full-time", "Part-time", "Contract", "Internship", "Temporary"],
        index=0
    )
    
    # UDS filters (hidden behind expander)
    with st.expander("Advanced Google Filters"):
        st.info("These are advanced Google-specific filters")
        date_posted = st.selectbox(
            "Date Posted",
            ["Any time", "Past 24 hours", "Past week", "Past month"],
            index=0
        )
        
        experience_level = st.selectbox(
            "Experience Level",
            ["Any", "Internship", "Entry level", "Associate", "Mid-Senior level", "Director", "Executive"],
            index=0
        )

# Main search form
with st.form("job_search_form"):
    col1, col2 = st.columns(2)
    with col1:
        keywords = st.text_input("Job Title or Keywords", placeholder="e.g. Software Engineer")
    with col2:
        location = st.text_input("Location", placeholder="e.g. New York or Remote")
    
    submitted = st.form_submit_button("Search Jobs")

# Function to build chips parameter
def build_chips():
    chips_parts = []
    
    # Date posted
    if date_posted != "Any time":
        if date_posted == "Past 24 hours":
            chips_parts.append("date_posted:today")
        elif date_posted == "Past week":
            chips_parts.append("date_posted:week")
        elif date_posted == "Past month":
            chips_parts.append("date_posted:month")
    
    # Job type
    if job_type != "Any":
        job_type_map = {
            "Full-time": "FULLTIME",
            "Part-time": "PARTTIME",
            "Contract": "CONTRACTOR",
            "Internship": "INTERN",
            "Temporary": "TEMPORARY"
        }
        chips_parts.append(f"employment_type:{job_type_map[job_type]}")
    
    # Experience level
    if experience_level != "Any":
        exp_map = {
            "Internship": "INTERNSHIP",
            "Entry level": "ENTRY_LEVEL",
            "Associate": "ASSOCIATE",
            "Mid-Senior level": "MID_LEVEL",
            "Director": "DIRECTOR",
            "Executive": "EXECUTIVE"
        }
        chips_parts.append(f"experience_level:{exp_map[experience_level]}")
    
    return ",".join(chips_parts) if chips_parts else None

def filter_jobs_by_platform(jobs, platforms, select_all):
    """Filter jobs to only include selected platforms"""
    if select_all or not platforms:
        return jobs
    return [job for job in jobs if any(platform.lower() in job['platform'].lower() for platform in platforms)]

# Display results
if submitted and (keywords or location):
    if not keywords:
        st.warning("Please enter at least one keyword to search for")
    else:
        with st.spinner("Searching for jobs..."):
            api = ScrapingDog()
            
            # Build chips parameter
            chips_value = build_chips()
            
            jobs = api.search_jobs(
                keywords=keywords,
                location=location,
                platform=None,
                count=count,
                days_ago=days_ago,
                country=country,
                lrad=str(search_radius) if (search_radius > 0 and not remote_only) else None,
                ltype="1" if remote_only else None,
                chips=chips_value,
                # next_page_token would be used for pagination in future
                # uds would be used for very specific Google filters
            )
            
            # Filter jobs based on selected platforms
            filtered_jobs = filter_jobs_by_platform(jobs, selected_platforms, select_all)
            
            if filtered_jobs:
                st.success(f"Found {len(filtered_jobs)} jobs matching your criteria")
                
                # Convert to DataFrame
                df = pd.DataFrame(filtered_jobs)
                
                # Reorder and select columns
                df = df[['title', 'company', 'location', 'date_posted', 'job_type', 'platform', 'apply_url']]
                
                # Rename columns for better display
                df.columns = ['Job Title', 'Company', 'Location', 'Posted', 'Job Type', 'Platform', 'Apply Link']
                
                # Add clickable links
                df['Apply'] = df['Apply Link'].apply(lambda x: f'{x}')
                
                # Display the DataFrame
                st.dataframe(
                    df[['Job Title', 'Company', 'Location', 'Posted', 'Job Type', 'Platform', 'Apply']],
                    column_config={
                        "Apply": st.column_config.LinkColumn("Apply"),
                        "Posted": st.column_config.TextColumn("Posted", width="small"),
                        "Job Type": st.column_config.TextColumn("Job Type", width="small"),
                        "Platform": st.column_config.TextColumn("Platform", width="small")
                    },
                    hide_index=True,
                    use_container_width=True,
                    height=600
                )
                
                # Download button
                csv = df.to_csv(index=False).encode('utf-8')
                st.download_button(
                    label="Download Results as CSV",
                    data=csv,
                    file_name='job_search_results.csv',
                    mime='text/csv'
                )
            else:
                st.warning("No jobs found matching your criteria. Try different filters.")
elif submitted:
    st.warning("Please enter at least one keyword to search for")

# Add some info about the app
st.markdown("---")
st.markdown("""
    ### About this Job Search App
    - **Powerful Search Filters:**
        - Country-specific searches
        - Remote job filtering
        - Location radius search
        - Job type filtering (Full-time, Part-time, etc.)
        - Experience level filtering
        - Date posted filtering
    - **Results Features:**
        - Multiple platforms searched simultaneously
        - Direct application links
        - Interactive data table
        - CSV export capability
    - **Powered by:** ScrapingDog API
""")

# Function to filter jobs by platform (must be defined for Streamlit)
def filter_jobs_by_platform(jobs, platforms, select_all):
    """Filter jobs to only include selected platforms"""
    if select_all or not platforms:
        return jobs
    return [job for job in jobs if any(platform.lower() in job['platform'].lower() for platform in platforms)]