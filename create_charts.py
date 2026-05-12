
import pandas as pd
import matplotlib.pyplot as plt

df = pd.read_csv('data/icu_patient_data.csv')

print("Creating charts for PowerPoint presentation...")
print("=" * 50)

fig, axes = plt.subplots(2, 2, figsize=(12, 10))

# Chart 1: Age distribution
axes[0,0].hist(df['age'], bins=30, color='steelblue', edgecolor='black')
axes[0,0].set_title('Age Distribution of ICU Patients', fontsize=12, fontweight='bold')
axes[0,0].set_xlabel('Age (years)')
axes[0,0].set_ylabel('Number of Patients')

# Chart 2: Sepsis vs Non-Sepsis
sepsis_count = [df['sepsis_flag'].sum(), len(df) - df['sepsis_flag'].sum()]
labels = ['Sepsis', 'No Sepsis']
colors = ['red', 'green']
axes[0,1].bar(labels, sepsis_count, color=colors, edgecolor='black')
axes[0,1].set_title('Sepsis Distribution', fontsize=12, fontweight='bold')
axes[0,1].set_ylabel('Number of Patients')

for i, v in enumerate(sepsis_count):
    axes[0,1].text(i, v + 100, str(v), ha='center', fontweight='bold')

# Chart 3: Heart Rate Comparison
heart_rates = [
    df[df['sepsis_flag']==1]['heart_rate_mean'].mean(),
    df[df['sepsis_flag']==0]['heart_rate_mean'].mean()
]
axes[1,0].bar(['Sepsis', 'No Sepsis'], heart_rates, color=['red', 'green'], edgecolor='black')
axes[1,0].set_title('Heart Rate Comparison', fontsize=12, fontweight='bold')
axes[1,0].set_ylabel('Heart Rate (bpm)')

# Add values on top of bars
for i, v in enumerate(heart_rates):
    axes[1,0].text(i, v + 1, f'{v:.1f}', ha='center', fontweight='bold')

# Chart 4: Temperature Comparison
temps = [
    df[df['sepsis_flag']==1]['temperature_mean'].mean(),
    df[df['sepsis_flag']==0]['temperature_mean'].mean()
]
axes[1,1].bar(['Sepsis', 'No Sepsis'], temps, color=['red', 'green'], edgecolor='black')
axes[1,1].set_title('Temperature Comparison', fontsize=12, fontweight='bold')
axes[1,1].set_ylabel('Temperature (°C)')

for i, v in enumerate(temps):
    axes[1,1].text(i, v + 0.1, f'{v:.1f}', ha='center', fontweight='bold')

plt.tight_layout()
plt.savefig('outputs/sepsis_chart.png', dpi=150, bbox_inches='tight')
print("Chart saved to: outputs/sepsis_chart.png")
print("File size:", end=" ")
