
import pandas as pd
import matplotlib.pyplot as plt

df = pd.read_csv('data/icu_patient_data.csv')

print("Creating mortality chart...")

fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 5))

# Chart 1: Overall Mortality
mortality_count = [
    len(df) - df['mortality_label'].sum(),
    df['mortality_label'].sum()
]
labels = ['Survived', 'Died']
colors = ['green', 'red']
ax1.bar(labels, mortality_count, color=colors, edgecolor='black')
ax1.set_title('Overall Mortality Rate', fontsize=12, fontweight='bold')
ax1.set_ylabel('Number of Patients')

for i, v in enumerate(mortality_count):
    ax1.text(i, v + 100, str(v), ha='center', fontweight='bold')

# Chart 2: Mortality by Sepsis Flag
sepsis_0_death = df[df['sepsis_flag']==0]['mortality_label'].mean() * 100
sepsis_1_death = df[df['sepsis_flag']==1]['mortality_label'].mean() * 100

ax2.bar(['No Sepsis', 'Sepsis'], [sepsis_0_death, sepsis_1_death], color=['green', 'red'], edgecolor='black')
ax2.set_title('Mortality Rate by Sepsis Flag', fontsize=12, fontweight='bold')
ax2.set_ylabel('Mortality Rate (%)')

for i, v in enumerate([sepsis_0_death, sepsis_1_death]):
    ax2.text(i, v + 1, f'{v:.1f}%', ha='center', fontweight='bold')

plt.tight_layout()
plt.savefig('outputs/mortality_chart.png', dpi=150, bbox_inches='tight')
print("Mortality chart saved to: outputs/mortality_chart.png")
