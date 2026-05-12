
import pandas as pd
import joblib

# Load the trained model
model = joblib.load('models/best_model.pkl')
print("✅ Model loaded successfully")

# Load test data
df = pd.read_csv('data/icu_patient_data.csv')

# Select same features as training
features = ['age', 'heart_rate_mean', 'temperature_mean', 'spo2_mean', 
            'respiratory_rate_mean', 'systolic_bp_mean', 'comorbidity_score',
            'lactate_mean', 'sofa_score', 'apache_score']

# Test on first 5 patients
test_patients = df[features].head(5)
actual_outcomes = df['mortality_label'].head(5)

print("\n" + "=" * 60)
print("TESTING MODEL ON 5 SAMPLE PATIENTS")
print("=" * 60)

predictions = model.predict(test_patients)
probabilities = model.predict_proba(test_patients)[:, 1]

for i in range(5):
    print(f"\nPatient {i+1}:")
    print(f"  Age: {test_patients.iloc[i]['age']:.0f}")
    print(f"  Heart Rate: {test_patients.iloc[i]['heart_rate_mean']:.0f} bpm")
    print(f"  Temperature: {test_patients.iloc[i]['temperature_mean']:.1f}°C")
    print(f"  Oxygen: {test_patients.iloc[i]['spo2_mean']:.0f}%")
    print(f"  Actual outcome: {'DIED' if actual_outcomes.iloc[i]==1 else 'SURVIVED'}")
    print(f"  Predicted outcome: {'DIED' if predictions[i]==1 else 'SURVIVED'}")
    print(f"  Risk probability: {probabilities[i]*100:.1f}%")
