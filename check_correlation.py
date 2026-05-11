
import pandas as pd

df = pd.read_csv('data/icu_patient_data.csv')

print('=' * 60)
print('SEPSIS FLAG CORRELATION ANALYSIS')
print('=' * 60)
print()

print('1. SEPSIS FLAG DISTRIBUTION:')
print('-' * 40)
sepsis_count = df['sepsis_flag'].value_counts()
print(f'Patients with sepsis_flag = 0: {sepsis_count[0]} ({sepsis_count[0]/len(df)*100:.1f}%)')
print(f'Patients with sepsis_flag = 1: {sepsis_count[1]} ({sepsis_count[1]/len(df)*100:.1f}%)')
print()

print('2. SEPSIS FLAG VS MORTALITY:')
print('-' * 40)
cross = pd.crosstab(df['sepsis_flag'], df['mortality_label'], normalize='index')
print('For patients with sepsis_flag = 0:')
print(f'  Survived (mortality=0): {cross.loc[0,0]*100:.1f}%')
print(f'  Died (mortality=1): {cross.loc[0,1]*100:.1f}%')
print()
print('For patients with sepsis_flag = 1:')
print(f'  Survived (mortality=0): {cross.loc[1,0]*100:.1f}%')
print(f'  Died (mortality=1): {cross.loc[1,1]*100:.1f}%')
print()

print('3. CORRELATION BETWEEN SEPSIS FLAG AND MORTALITY:')
print('-' * 40)
correlation = df['sepsis_flag'].corr(df['mortality_label'])
print(f'Correlation coefficient: {correlation:.3f}')
print('Interpretation:')
if correlation > 0.5:
    print('  Strong positive correlation - Sepsis patients more likely to die')
elif correlation > 0.3:
    print('  Moderate correlation - Sepsis related to mortality')
elif correlation > 0.1:
    print('  Weak correlation - Some relationship')
else:
    print('  Very weak correlation - Sepsis flag not strongly related to death')
print()

print('4. VITAL SIGNS BY SEPSIS FLAG:')
print('-' * 40)
vitals = ['age', 'heart_rate_mean', 'temperature_mean', 'spo2_mean']
for vital in vitals:
    sepsis_mean = df[df['sepsis_flag']==1][vital].mean()
    no_sepsis_mean = df[df['sepsis_flag']==0][vital].mean()
    diff = sepsis_mean - no_sepsis_mean
    print(f'{vital}:')
    print(f'  Sepsis=1: {sepsis_mean:.1f} | Sepsis=0: {no_sepsis_mean:.1f} | Difference: {diff:+.1f}')
