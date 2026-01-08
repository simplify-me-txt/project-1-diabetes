import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import RandomForestClassifier
from xgboost import XGBClassifier
from sklearn.metrics import accuracy_score, classification_report
import joblib

print("🚀 Starting Multi-Model Training...")
print("=" * 60)

# Load dataset (PIMA Indian Diabetes Dataset)
df = pd.read_csv("diabetes.csv")
print(f"✅ Dataset loaded: {df.shape[0]} samples, {df.shape[1]} features")

X = df.drop("Outcome", axis=1)
y = df["Outcome"]

# Scale features
scaler = StandardScaler()
X_scaled = scaler.fit_transform(X)

# Split data
X_train, X_test, y_train, y_test = train_test_split(
    X_scaled, y, test_size=0.2, random_state=42
)

print(f"\n📊 Training set: {X_train.shape[0]} samples")
print(f"📊 Test set: {X_test.shape[0]} samples")
print("\n" + "=" * 60)

# === MODEL 1: Logistic Regression ===
print("\n🔹 Training Model 1: Logistic Regression")
model_lr = LogisticRegression(max_iter=500, random_state=42)
model_lr.fit(X_train, y_train)
y_pred_lr = model_lr.predict(X_test)
accuracy_lr = accuracy_score(y_test, y_pred_lr)
print(f"   ✓ Accuracy: {accuracy_lr:.4f} ({accuracy_lr*100:.2f}%)")

# === MODEL 2: Random Forest ===
print("\n🔹 Training Model 2: Random Forest")
model_rf = RandomForestClassifier(
    n_estimators=100,
    max_depth=10,
    random_state=42,
    n_jobs=-1
)
model_rf.fit(X_train, y_train)
y_pred_rf = model_rf.predict(X_test)
accuracy_rf = accuracy_score(y_test, y_pred_rf)
print(f"   ✓ Accuracy: {accuracy_rf:.4f} ({accuracy_rf*100:.2f}%)")

# === MODEL 3: XGBoost ===
print("\n🔹 Training Model 3: XGBoost")
model_xgb = XGBClassifier(
    n_estimators=100,
    max_depth=6,
    learning_rate=0.1,
    random_state=42,
    eval_metric='logloss'
)
model_xgb.fit(X_train, y_train)
y_pred_xgb = model_xgb.predict(X_test)
accuracy_xgb = accuracy_score(y_test, y_pred_xgb)
print(f"   ✓ Accuracy: {accuracy_xgb:.4f} ({accuracy_xgb*100:.2f}%)")

# === ENSEMBLE VOTING ===
print("\n" + "=" * 60)
print("🎯 Ensemble Voting System")
print("=" * 60)

# Majority voting
y_pred_ensemble = []
for i in range(len(y_test)):
    votes = [y_pred_lr[i], y_pred_rf[i], y_pred_xgb[i]]
    prediction = 1 if sum(votes) >= 2 else 0
    y_pred_ensemble.append(prediction)

accuracy_ensemble = accuracy_score(y_test, y_pred_ensemble)
print(f"\n📈 Ensemble Accuracy: {accuracy_ensemble:.4f} ({accuracy_ensemble*100:.2f}%)")

# Save all models and scaler
print("\n" + "=" * 60)
print("💾 Saving models...")
joblib.dump(model_lr, "diabetes_model_lr.pkl")
print("   ✓ Logistic Regression saved")
joblib.dump(model_rf, "diabetes_model_rf.pkl")
print("   ✓ Random Forest saved")
joblib.dump(model_xgb, "diabetes_model_xgb.pkl")
print("   ✓ XGBoost saved")
joblib.dump(scaler, "scaler.pkl")
print("   ✓ Scaler saved")

# Also save the old model for backward compatibility
joblib.dump(model_lr, "diabetes_model.pkl")
print("   ✓ Legacy model saved")

print("\n" + "=" * 60)
print("✅ Multi-Model AI System Training Complete!")
print("=" * 60)
print("\n📊 Model Performance Summary:")
print(f"   • Logistic Regression: {accuracy_lr*100:.2f}%")
print(f"   • Random Forest:       {accuracy_rf*100:.2f}%")
print(f"   • XGBoost:             {accuracy_xgb*100:.2f}%")
print(f"   • Ensemble (Voting):   {accuracy_ensemble*100:.2f}%")
print("\n🎉 All models ready for production!\n")
