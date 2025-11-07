# main.py
# Step 1: Import libraries
import pandas as pd
import numpy as np
import joblib
import matplotlib.pyplot as plt

# Step 2: Load the dataset
df = pd.read_csv('data/Metro_Interstate_Traffic_Volume.csv')

print("✅ Data Loaded Successfully!")
print(df.head())
print("Shape:", df.shape)

# Step 3: Check for missing values
print("\nMissing Values:")
print(df.isnull().sum())

# Step 4: Clean the data
df = df.drop_duplicates().copy()
df['date_time'] = pd.to_datetime(df['date_time'])
df['holiday'] = df['holiday'].fillna('None')
df['weather_main'] = df['weather_main'].fillna('Clear')
df['weather_description'] = df['weather_description'].fillna('clear sky')
df['temp'] = df['temp'] - 273.15   # Kelvin → Celsius

# Step 5: Extract useful time features
df['hour'] = df['date_time'].dt.hour
df['weekday'] = df['date_time'].dt.weekday
df['month'] = df['date_time'].dt.month

# Step 6: Encode cyclical time features
df['hour_sin'] = np.sin(2 * np.pi * df['hour'] / 24)
df['hour_cos'] = np.cos(2 * np.pi * df['hour'] / 24)

# Step 7: Keep only useful columns
df = df[['temp', 'rain_1h', 'snow_1h', 'clouds_all',
         'hour_sin', 'hour_cos', 'weekday', 'month', 'traffic_volume']]

# Step 8: Add congestion level (classification labels)
df['congestion_level'] = pd.cut(
    df['traffic_volume'],
    bins=[-1, 3000, 6000, 1e9],   # -1 to include 0, and large upper bound
    labels=['Low', 'Moderate', 'High']
)

# Step 9: Show final cleaned data
print("\n✅ Cleaned Data:")
print(df.head())
print(df.info())

# -----------------------------------------
# STEP 10: MACHINE LEARNING (REGRESSION)
# -----------------------------------------
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
from sklearn.ensemble import RandomForestRegressor, ExtraTreesRegressor
from sklearn.linear_model import LinearRegression
from xgboost import XGBRegressor

print("\n🚀 Training Regression Models...")

# Features (X) and Target (y) for regression
X = df.drop(columns=['traffic_volume', 'congestion_level'])
y = df['traffic_volume']

# Save feature column order for later (used by Streamlit)
feature_columns = X.columns.tolist()
joblib.dump(feature_columns, 'feature_columns.pkl')
print("🧩 Saved feature column order to feature_columns.pkl:", feature_columns)

# Train-test split (80% train, 20% test)
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

# Define regression models
models = {
    "Linear Regression": LinearRegression(),
    "Random Forest": RandomForestRegressor(n_estimators=100, random_state=42),
    "Extra Trees": ExtraTreesRegressor(n_estimators=100, random_state=42),
    "XGBoost": XGBRegressor(n_estimators=100, random_state=42, objective='reg:squarederror')
}

results = {}

# Train and evaluate each regression model
for name, model in models.items():
    model.fit(X_train, y_train)
    y_pred = model.predict(X_test)

    mae = mean_absolute_error(y_test, y_pred)
    mse = mean_squared_error(y_test, y_pred)
    r2 = r2_score(y_test, y_pred)

    results[name] = {"MAE": mae, "MSE": mse, "R2": r2}
    print(f"\n✅ {name} Results:")
    print(f"MAE: {mae:.2f}")
    print(f"MSE: {mse:.2f}")
    print(f"R2 Score: {r2:.2f}")

# Save regression results
results_df = pd.DataFrame([
    {"Model": name, "MAE": vals["MAE"], "MSE": vals["MSE"], "R2": vals["R2"]}
    for name, vals in results.items()
])
results_df.to_csv("model_results.csv", index=False)
print("\n📊 Regression model results saved to model_results.csv")

# Save best regression model
best_model_name = max(results, key=lambda x: results[x]['R2'])
best_model = models[best_model_name]
joblib.dump(best_model, 'best_ml_model.pkl')
print(f"\n🏆 Best Regression Model Saved: {best_model_name}")

# -----------------------------------------
# STEP 11: MACHINE LEARNING (CLASSIFICATION)
# -----------------------------------------
from sklearn.metrics import accuracy_score, classification_report, confusion_matrix
from sklearn.ensemble import RandomForestClassifier
from xgboost import XGBClassifier
from sklearn.preprocessing import LabelEncoder

print("\n🚦 Training Classification Models...")

# Drop rows with missing congestion labels
df_cls = df.dropna(subset=['congestion_level']).copy()

# Encode 'Low', 'Moderate', 'High' -> 0, 1, 2
le = LabelEncoder()
df_cls['congestion_level_encoded'] = le.fit_transform(df_cls['congestion_level'])

# X and y for classification (do NOT include any encoded label column as feature)
X_cls = df_cls[['temp', 'rain_1h', 'snow_1h', 'clouds_all', 'hour_sin', 'hour_cos', 'weekday', 'month']]
y_cls = df_cls['congestion_level_encoded']

X_train_cls, X_test_cls, y_train_cls, y_test_cls = train_test_split(
    X_cls, y_cls, test_size=0.2, random_state=42, stratify=y_cls
)

classifiers = {
    "Random Forest Classifier": RandomForestClassifier(n_estimators=100, random_state=42),
    "XGBoost Classifier": XGBClassifier(n_estimators=100, random_state=42, use_label_encoder=False, eval_metric='mlogloss')
}

cls_results = {}

for name, clf in classifiers.items():
    clf.fit(X_train_cls, y_train_cls)
    y_pred_cls = clf.predict(X_test_cls)

    acc = accuracy_score(y_test_cls, y_pred_cls)
    cls_results[name] = {"Accuracy": acc}
    print(f"\n✅ {name} Accuracy: {acc:.2f}")
    print(classification_report(y_test_cls, y_pred_cls))
    print(confusion_matrix(y_test_cls, y_pred_cls))

# Save classification results
cls_results_df = pd.DataFrame([
    {"Model": name, "Accuracy": vals["Accuracy"]}
    for name, vals in cls_results.items()
])
cls_results_df.to_csv("classification_results.csv", index=False)
print("\n📊 Classification model results saved to classification_results.csv")

# Save best classification model and encoder
best_cls_name = max(cls_results, key=lambda x: cls_results[x]['Accuracy'])
best_cls_model = classifiers[best_cls_name]
joblib.dump(best_cls_model, 'best_cls_model.pkl')
joblib.dump(le, 'label_encoder.pkl')  # Save encoder
print(f"\n🏆 Best Classification Model Saved: {best_cls_name}")
print("\n🧩 Label Encoder Saved: label_encoder.pkl")
