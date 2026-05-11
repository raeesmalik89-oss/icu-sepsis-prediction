
import pandas as pd

df = pd.read_csv('data/icu_patient_data.csv')

sepsis = df[df['sepsis_flag'] == 1]
no_sepsis = df[df['sepsis_flag'] == 0]

print('=' * 50)
print('SEPSIS VS NON-SEPSIS COMPARISON')
print('=' * 50)
print()

print('AGE:')
print(f'  Sepsis patients: {sepsis["age"].mean():.1f} years')
print(f'  Non-sepsis patients: {no_sepsis["age"].mean():.1f} years')
print()

print('HEART RATE:')
print(f'  Sepsis patients: {sepsis["heart_rate_mean"].mean():.1f} bpm')
print(f'  Non-sepsis patients: {no_sepsis["heart_rate_mean"].mean():.1f} bpm')
print()

print('TEMPERATURE:')
print(f'  Sepsis patients: {sepsis["temperature_mean"].mean():.1f} °C')
print(f'  Non-sepsis patients: {no_sepsis["temperature_mean"].mean():.1f} °C')
print()

print('OXYGEN LEVEL:')
print(f'  Sepsis patients: {sepsis["spo2_mean"].mean():.1f} %')
print(f'  Non-sepsis patients: {no_sepsis["spo2_mean"].mean():.1f} %')
