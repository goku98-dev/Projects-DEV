import pandas as pd
import numpy as np

from data_loader import load_table
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LinearRegression
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_absolute_error, r2_score

# --------------------------------------------------
# 1. LOAD DATA
# --------------------------------------------------
df = load_table("analytical_view")

print("Total rows loaded:", len(df))

# Drop rows with missing values (important after LEFT JOIN)
df = df.dropna()

# --------------------------------------------------
# 2. DEFINE TARGET & FEATURES
# --------------------------------------------------
y = df["profit"]

X = df[
    [
        "selling_value",
        "purchase_value",
        "contract_duration",
        "segment"
    ]
]

# One-hot encode categorical variable
X = pd.get_dummies(X, columns=["segment"], drop_first=True)

print("\nFeature columns:")
print(X.columns)

# --------------------------------------------------
# 3. TRAIN–TEST SPLIT
# --------------------------------------------------
X_train, X_test, y_train, y_test = train_test_split(
    X, y,
    test_size=0.2,
    random_state=42
)

print("\nTrain size:", len(X_train))
print("Test size:", len(X_test))

# --------------------------------------------------
# 4. LINEAR REGRESSION (BASELINE)
# --------------------------------------------------
lr_model = LinearRegression()
lr_model.fit(X_train, y_train)

lr_preds = lr_model.predict(X_test)

print("\n--- Linear Regression Results ---")
print("MAE:", mean_absolute_error(y_test, lr_preds))
print("R² :", r2_score(y_test, lr_preds))

# Coefficients
lr_coefficients = pd.DataFrame(
    {
        "Feature": X_train.columns,
        "Coefficient": lr_model.coef_
    }
).sort_values(by="Coefficient", ascending=False)

print("\nLinear Regression Coefficients:")
print(lr_coefficients)

# --------------------------------------------------
# 5. RANDOM FOREST REGRESSION
# --------------------------------------------------
rf_model = RandomForestRegressor(
    n_estimators=200,
    max_depth=8,
    random_state=42
)

rf_model.fit(X_train, y_train)

rf_preds = rf_model.predict(X_test)

print("\n--- Random Forest Results ---")
print("MAE:", mean_absolute_error(y_test, rf_preds))
print("R² :", r2_score(y_test, rf_preds))

# Feature importance
rf_importance = pd.Series(
    rf_model.feature_importances_,
    index=X_train.columns
).sort_values(ascending=False)

print("\nRandom Forest Feature Importance:")
print(rf_importance)

# --------------------------------------------------
# 6. SAMPLE PREDICTION (BOTH MODELS)
# --------------------------------------------------
sample = X_test.iloc[[0]]
actual_profit = y_test.iloc[0]

# Predictions
lr_predicted_profit = lr_model.predict(sample)[0]
rf_predicted_profit = rf_model.predict(sample)[0]

print("\n--- Sample Prediction (Model Comparison) ---")
print("Actual Profit           :", actual_profit)
print("Linear Regression Profit:", lr_predicted_profit)
print("Random Forest Profit    :", rf_predicted_profit)

