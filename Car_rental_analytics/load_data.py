from data_loader import load_table

analytics_df = load_table("analytical_view")

print(analytics_df.head())
print("Rows:", len(analytics_df))

