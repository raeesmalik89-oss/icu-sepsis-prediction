
import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score, roc_auc_score, confusion_matrix
import joblib
import warnings
warnings.filterwarnings('ignore')

print("=" * 60)
print("BALANCED MODEL TRAINING - WITH CLASS WEIGHT")
print("=" * 60)

df = pd.read_csv('data/icu_patient_data.csv')
print(f"Loaded {len(df)} patients")

features = ['age', 'heart_rate_mean', 'temperature_mean', 'spo2_mean', 
            'respiratory_rate_mean', 'systolic_bp_mean', 'comorbidity_score',
            'lactate_mean', 'sofa_score', 'apache_score']

X = df[features]
y = df['mortality_label']

survived = (y == 0).sum()
died = (y == 1).sum()
print(f"Survived: {survived} ({survived/len(y)*100:.1f}%)")
print(f"Died: {died} ({died/len(y)*100:.1f}%)")

# Calculate class weight (give more importance to death cases)
class_weight = {0: 1.0, 1: survived/died}
print(f"Class weight: Deaths are {class_weight[1]:.1f}x more important")

X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42, stratify=y)

models = {
    'Random Forest (Balanced)': RandomForestClassifier(
        n_estimators=100, 
        class_weight='balanced', 
        random_state=42
    ),
    'Logistic Regression (Balanced)': LogisticRegression(
        class_weight='balanced', 
        max_iter=1000, 
        random_state=42
    )
}

try:
    from xgboost import XGBClassifier
    models['XGBoost (Balanced)'] = XGBClassifier(
        n_estimators=100, 
        scale_pos_weight=survived/died,
        random_state=42, 
        use_label_encoder=False, 
        eval_metric='logloss'
    )
except:
    print("XGBoost not available")

results = []

print("\n" + "=" * 60)
print("IMPROVED MODEL RESULTS")
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
    
    cm = confusion_matrix(y_test, y_pred)
    
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
    print(f"  ROC-AUC: {auc*100:.1f}%")
    print(f"  Confusion Matrix:")
    print(f"    True Survived: {cm[0,0]} | False Death: {cm[0,1]}")
    print(f"    False Survived: {cm[1,0]} | True Death: {cm[1,1]}")
    
    if name == 'Random Forest (Balanced)':
        joblib.dump(model, 'models/balanced_model.pkl')
        print(f"\n✅ Saved: models/balanced_model.pkl")

results_df = pd.DataFrame(results)
results_df.to_csv('outputs/balanced_model_results.csv', index=False)
print("\n" + "=" * 60)
print("RESULTS SAVED: outputs/balanced_model_results.csv")
print("=" * 60)

# Feature importance
best_model = models['Random Forest (Balanced)']
importances = best_model.feature_importances_
print("\nFEATURE IMPORTANCE (What matters most for prediction):")
for feat, imp in sorted(zip(features, importances), key=lambda x: x[1], reverse=True):
    print(f"  {feat}: {imp*100:.1f}%")
