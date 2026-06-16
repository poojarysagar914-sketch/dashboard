from sqlalchemy import create_engine

# Connect to your local MySQL Database
# Format: mysql+mysqlconnector://username:password@host:port/database_name
engine = create_engine("mysql+mysqlconnector://root:password@localhost/movie_db")

# Push the DataFrame to a MySQL table named 'popular_movies'
df.to_sql(name="popular_movies", con=engine, if_exists="replace", index=False)
print("Data successfully loaded into MySQL!")
