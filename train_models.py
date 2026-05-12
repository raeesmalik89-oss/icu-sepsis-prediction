
import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score, roc_auc_score
import joblib
import warnings
warnings.filterwarnings('ignore')

print("=" * 60)
print("PHASE 3: TRAINING MACHINE LEARNING MODELS")
print("=" * 60)

# Load data
df = pd.read_csv('data/icu_patient_data.csv')
print(f"\nLoaded {len(df)} patient records")

# Select features for training
features = ['age', 'heart_rate_mean', 'temperature_mean', 'spo2_mean', 
            'respiratory_rate_mean', 'systolic_bp_mean', 'comorbidity_score',
            'lactate_mean', 'sofa_score', 'apache_score']

X = df[features]
y = df['mortality_label']

print(f"Features used: {len(features)} clinical measurements")
print(f"Target: mortality_label (0=survived, 1=died)")
print(f"Death rate in dataset: {y.mean()*100:.1f}%")

# Split data
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42, stratify=y)
print(f"\nTraining set: {len(X_train)} patients")
print(f"Test set: {len(X_test)} patients")

# Train models
models = {
    'Random Forest': RandomForestClassifier(n_estimators=100, random_state=42),
    'Logistic Regression': LogisticRegression(max_iter=1000, random_state=42)
}

try:
    from xgboost import XGBClassifier
    models['XGBoost'] = XGBClassifier(n_estimators=100, random_state=42, use_label_encoder=False, eval_metric='logloss')
except:
    print("XGBoost not available, continuing with 2 models")

results = []

print("\n" + "=" * 60)
print("TRAINING RESULTS")
print("=" * 60)

for name, model in models.items():
    print(f"\nTraining {name}...")
    model.fit(X_train, y_train)
    y_pred = model.predict(X_test)
    y_proba = model.predict_proba(X_test)[:, 1]
    
    accuracy = accuracy_score(y_test, y_pred)
    precision = precision_score(y_test, y_pred)
    recall = recall_score(y_test, y_pred)
    f1 = f1_score(y_test, y_pred)
    auc = roc_auc_score(y_test, y_proba)
    
    results.append({
        'Model': name,
        'Accuracy': f"{accuracy*100:.1f}%",
        'Precision': f"{precision*100:.1f}%",
        'Recall': f"{recall*100:.1f}%",
        'F1 Score': f"{f1*100:.1f}%",
        'ROC-AUC': f"{auc*100:.1f}%"
    })
    
    print(f"  Accuracy: {accuracy*100:.1f}%")
    print(f"  Precision: {precision*100:.1f}%")
    print(f"  Recall: {recall*100:.1f}%")
    print(f"  F1 Score: {f1*100:.1f}%")
    print(f"  ROC-AUC: {auc*100:.1f}%")
    
    # Save best model
    if name == 'Random Forest':
        joblib.dump(model, 'models/best_model.pkl')
        print(f"\n✅ Best model saved: models/best_model.pkl")

# Save results to CSV
results_df = pd.DataFrame(results)
results_df.to_csv('outputs/model_results.csv', index=False)
print("\n" + "=" * 60)
print("RESULTS SAVED")
print("=" * 60)
print(f"📁 outputs/model_results.csv")
