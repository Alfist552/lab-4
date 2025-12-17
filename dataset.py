import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

movies = pd.read_csv('tmdb_5000_movies.csv')
df = movies.copy()
df = df[(df['budget'] > 0) & (df['revenue'] > 0)].copy()

budgets_array = np.array(df['budget'])
revenues_array = np.array(df['revenue'])

bins_budget = np.linspace(0, 200_000_000, 21)
bins_revenue = np.arange(0, 500_000_001, 25_000_000)

fig, axes = plt.subplots(1, 2, figsize=(14, 6))

ax1 = axes[0]
counts, bins, patches = ax1.hist(budgets_array, bins=bins_budget,
                                alpha=0.7, color='skyblue',
                                edgecolor='navy', linewidth=1)
median_budget = np.median(budgets_array)
ax1.axvline(median_budget, color='red', linestyle='--', linewidth=2)
ax1.set_title('Распределение бюджетов')
ax1.set_xlabel('Бюджет (млн $)')
ax1.set_ylabel('Количество фильмов')
ax1.grid(True, alpha=0.3, axis='y')

ax2 = axes[1]
counts2, bins2, patches2 = ax2.hist(revenues_array, bins=bins_revenue,
                                   alpha=0.7, color='lightgreen',
                                   edgecolor='darkgreen', linewidth=1)
median_revenue = np.median(revenues_array)
ax2.axvline(median_revenue, color='red', linestyle='--', linewidth=2)
ax2.set_title('Распределение сборов')
ax2.set_xlabel('Сборы (млн $)')
ax2.set_ylabel('Количество фильмов')
ax2.grid(True, alpha=0.3, axis='y')

plt.tight_layout()
plt.show()