
import pandas as pd

df = pd.read_csv('data/icu_patient_data.csv')

print('=' * 50)
print('DATA STATISTICS SUMMARY')
print('=' * 50)
print()

print('Patient Age Statistics:')
print(f'  Average age: {df["age"].mean():.1f} years')
print(f'  Youngest: {df["age"].min():.0f} years')
print(f'  Oldest: {df["age"].max():.0f} years')
print()

print('Heart Rate Statistics:')
print(f'  Average: {df["heart_rate_mean"].mean():.1f} bpm')
print()

print('Temperature Statistics:')
print(f'  Average: {df["temperature_mean"].mean():.1f} °C')
print()

print('Oxygen Level (SpO2):')
print(f'  Average: {df["spo2_mean"].mean():.1f} %')
