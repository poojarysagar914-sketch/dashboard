import streamlit as st
import pandas as pd
import sqlite3
import plotly.express as px

# 1. Page Configuration
st.set_page_config(page_title="Movie Rating Dashboard", layout="wide")
st.title("🎬 Bollywood Movie Rating Dashboard")
st.markdown("Analyzing ratings, box office performance, and cast insights")

# 2. Load CSV Data into an In-Memory SQL Database
@st.cache_resource
def load_data_to_sql():
    # Read CSV
    csv_file = "movies.csv" 
    df = pd.read_csv(csv_file)
    
    # Create in-memory SQL database
    conn = sqlite3.connect(':memory:', check_same_thread=False)
    
    # Write data to a SQL table named 'movies'
    df.to_sql('movies', conn, index=False, if_exists='replace')
    return conn

try:
    conn = load_data_to_sql()

    # 3. Sidebar Filters
    st.sidebar.header("🎯 Filters")
    
    genres = pd.read_sql("SELECT DISTINCT genre FROM movies ORDER BY genre", conn)["genre"].tolist()
    selected_genre = st.sidebar.selectbox("Select Genre", ["All"] + genres)

    directors = pd.read_sql("SELECT DISTINCT director FROM movies ORDER BY director", conn)["director"].tolist()
    selected_director = st.sidebar.selectbox("Select Director", ["All"] + directors)

    actors = pd.read_sql("SELECT DISTINCT lead_actor FROM movies ORDER BY lead_actor", conn)["lead_actor"].tolist()
    selected_actor = st.sidebar.selectbox("Select Lead Actor", ["All"] + actors)

    verdict_options = pd.read_sql("SELECT DISTINCT verdict FROM movies ORDER BY verdict", conn)["verdict"].tolist()
    selected_verdict = st.sidebar.selectbox("Select Verdict", ["All"] + verdict_options)

    # Year range filter
    year_range = st.sidebar.slider("Release Year Range", 2009, 2025, (2009, 2025))

    # 4. Build the SQL Query based on Filters
    query = "SELECT * FROM movies WHERE 1=1"
    
    if selected_genre != "All":
        query += f" AND genre = '{selected_genre}'"
    if selected_director != "All":
        query += f" AND director = '{selected_director}'"
    if selected_actor != "All":
        query += f" AND lead_actor = '{selected_actor}'"
    if selected_verdict != "All":
        query += f" AND verdict = '{selected_verdict}'"
    
    query += f" AND release_year BETWEEN {year_range[0]} AND {year_range[1]}"

    # Execute main query
    df_filtered = pd.read_sql(query, conn)

    # 5. SQL Aggregations for Key Metrics (KPIs)
    kpi_query = """
        SELECT 
            COUNT(*) as Total_Movies,
            ROUND(AVG(imdb_rating), 2) as Avg_Rating,
            ROUND(AVG(box_office_in_crores), 2) as Avg_Box_Office
        FROM movies
        WHERE 1=1
    """
    
    if selected_genre != "All":
        kpi_query += f" AND genre = '{selected_genre}'"
    if selected_director != "All":
        kpi_query += f" AND director = '{selected_director}'"
    if selected_actor != "All":
        kpi_query += f" AND lead_actor = '{selected_actor}'"
    if selected_verdict != "All":
        kpi_query += f" AND verdict = '{selected_verdict}'"
    
    kpi_query += f" AND release_year BETWEEN {year_range[0]} AND {year_range[1]}"
        
    kpi_df = pd.read_sql(kpi_query, conn)

    # Display KPI Cards
    col1, col2, col3 = st.columns(3)
    col1.metric("🎥 Total Movies", f"{int(kpi_df['Total_Movies'].values[0])}")
    col2.metric("⭐ Avg Rating", f"{kpi_df['Avg_Rating'].values[0]:.1f}/10")
    col3.metric("💰 Avg Box Office", f"₹{kpi_df['Avg_Box_Office'].values[0]:.0f} Cr")

    st.markdown("---")

    # 6. Charts
    # Chart 1: IMDB Rating Distribution
    chart1_query = """
        SELECT ROUND(imdb_rating, 1) as Rating, COUNT(*) as Count 
        FROM movies
        WHERE 1=1
    """
    if selected_genre != "All":
        chart1_query += f" AND genre = '{selected_genre}'"
    if selected_director != "All":
        chart1_query += f" AND director = '{selected_director}'"
    if selected_actor != "All":
        chart1_query += f" AND lead_actor = '{selected_actor}'"
    if selected_verdict != "All":
        chart1_query += f" AND verdict = '{selected_verdict}'"
    chart1_query += f" AND release_year BETWEEN {year_range[0]} AND {year_range[1]}"
    chart1_query += " GROUP BY Rating ORDER BY Rating"
    
    df_chart1 = pd.read_sql(chart1_query, conn)
    fig_rating = px.bar(df_chart1, x="Rating", y="Count", title="Rating Distribution", template="plotly_white", color="Count", color_continuous_scale="Blues")

    # Chart 2: Box Office by Genre
    chart2_query = """
        SELECT genre, AVG(box_office_in_crores) as Avg_Box_Office, COUNT(*) as Movie_Count
        FROM movies
        WHERE 1=1
    """
    if selected_genre != "All":
        chart2_query += f" AND genre = '{selected_genre}'"
    if selected_director != "All":
        chart2_query += f" AND director = '{selected_director}'"
    if selected_actor != "All":
        chart2_query += f" AND lead_actor = '{selected_actor}'"
    if selected_verdict != "All":
        chart2_query += f" AND verdict = '{selected_verdict}'"
    chart2_query += f" AND release_year BETWEEN {year_range[0]} AND {year_range[1]}"
    chart2_query += " GROUP BY genre ORDER BY Avg_Box_Office DESC"
    
    df_chart2 = pd.read_sql(chart2_query, conn)
    fig_boxoffice = px.bar(df_chart2, x="genre", y="Avg_Box_Office", title="Avg Box Office by Genre", template="plotly_white", color="Avg_Box_Office", color_continuous_scale="Greens")

    # Chart 3: Rating vs Box Office
    fig_scatter = px.scatter(df_filtered, x="imdb_rating", y="box_office_in_crores", 
                             color="verdict", size="budget_in_crores", hover_name="movie_name",
                             title="Rating vs Box Office Performance", template="plotly_white")

    # Chart 4: Movies by Verdict
    chart4_query = """
        SELECT verdict, COUNT(*) as Count
        FROM movies
        WHERE 1=1
    """
    if selected_genre != "All":
        chart4_query += f" AND genre = '{selected_genre}'"
    if selected_director != "All":
        chart4_query += f" AND director = '{selected_director}'"
    if selected_actor != "All":
        chart4_query += f" AND lead_actor = '{selected_actor}'"
    if selected_verdict != "All":
        chart4_query += f" AND verdict = '{selected_verdict}'"
    chart4_query += f" AND release_year BETWEEN {year_range[0]} AND {year_range[1]}"
    chart4_query += " GROUP BY verdict"
    
    df_chart4 = pd.read_sql(chart4_query, conn)
    fig_verdict = px.pie(df_chart4, values="Count", names="verdict", title="Movies by Verdict")

    # Display Charts
    col_chart1, col_chart2 = st.columns(2)
    col_chart1.plotly_chart(fig_rating, use_container_width=True)
    col_chart2.plotly_chart(fig_boxoffice, use_container_width=True)

    col_chart3, col_chart4 = st.columns(2)
    col_chart3.plotly_chart(fig_scatter, use_container_width=True)
    col_chart4.plotly_chart(fig_verdict, use_container_width=True)

    # 7. Show Raw Data Table
    st.subheader("📋 Filtered Movies Data")
    st.dataframe(df_filtered, use_container_width=True)

except Exception as e:
    st.error(f"Please ensure 'movies.csv' exists in the folder. Error: {e}")