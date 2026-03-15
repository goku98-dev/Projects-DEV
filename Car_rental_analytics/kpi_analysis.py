import pandas as pd
import matplotlib.pyplot as plt
from data_loader import load_table

# -------------------------
# LOAD DATA
# -------------------------
df = load_table("analytical_view")

print("Rows loaded:", len(df))

# -------------------------
# KPI 1: TOTAL REVENUE & PROFIT
# -------------------------
total_revenue = df["selling_value"].sum()
total_profit = df["profit"].sum()

print(f"\nTotal Revenue: {total_revenue:.2f}")
print(f"Total Profit: {total_profit:.2f}")

# -------------------------
# KPI 2: PROFIT MARGIN BY SEGMENT
# -------------------------
segment_summary = (
    df.groupby("segment")
    .agg(
        revenue=("selling_value", "sum"),
        profit=("profit", "sum"),
        contracts=("contract_id", "count")
    )
)

segment_summary["profit_margin_%"] = (
    segment_summary["profit"] / segment_summary["revenue"] * 100
)

print("\nSegment Profitability:")
print(segment_summary)

# -------------------------
# KPI 3: REVENUE PER CONTRACT
# -------------------------
segment_summary["revenue_per_contract"] = (
    segment_summary["revenue"] / segment_summary["contracts"]
)

# -------------------------
# KPI 4: SEGMENT EFFICIENCY SCORE
# -------------------------
duration_by_segment = (
    df.groupby("segment")["contract_duration"].sum()
)

segment_summary["efficiency_score"] = (
    segment_summary["revenue"] / duration_by_segment
)

# -------------------------
# KPI 5: VEHICLE ROI
# -------------------------
vehicle_performance = (
    df.groupby(["vehicle_id", "desc_vehicle"])
    .agg(
        total_revenue=("selling_value", "sum"),
        purchase_value=("purchase_value", "max"),
        total_profit=("profit", "sum")
    )
)

vehicle_performance["roi"] = (
    (vehicle_performance["total_revenue"] - vehicle_performance["purchase_value"])
    / vehicle_performance["purchase_value"]
)

# -------------------------
# TOP & BOTTOM VEHICLES
# -------------------------
top_vehicles = vehicle_performance.sort_values("total_profit", ascending=False).head(5)
bottom_vehicles = vehicle_performance.sort_values("total_profit").head(5)

print("\nTop 5 Vehicles by Profit:")
print(top_vehicles)

print("\nBottom 5 Vehicles by Profit:")
print(bottom_vehicles)

# -------------------------
# VISUALIZATION
# -------------------------
segment_summary["profit_margin_%"].plot(kind="bar")
plt.title("Profit Margin by Customer Segment")
plt.ylabel("Profit Margin (%)")
plt.xlabel("Segment")
plt.tight_layout()
plt.show()
