import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

df = pd.read_csv('tmdb_5000_movies.csv')
df = df[(df['budget'] > 0) & (df['revenue'] > 0)].copy()

print("="*60)
print("ПРОВЕРКА СТАТИСТИЧЕСКОЙ ГИПОТЕЗЫ")
print("="*60)

print("H₀ (нулевая гипотеза): НЕТ корреляции между бюджетом и сборами")
print("H₁ (альтернативная гипотеза): ЕСТЬ положительная корреляция")
print("Уровень значимости: α = 0.05")

actual_corr = df['budget'].corr(df['revenue'])
print(f"\nФАКТИЧЕСКАЯ КОРРЕЛЯЦИЯ: r = {actual_corr:.4f}")

if actual_corr >= 0.7:
    strength = "СИЛЬНАЯ"
elif actual_corr >= 0.5:
    strength = "УМЕРЕННАЯ"
elif actual_corr >= 0.3:
    strength = "СЛАБАЯ"
else:
    strength = "ОЧЕНЬ СЛАБАЯ"

print(f"Качественно: {strength} положительная корреляция")

print(f"\nПЕРЕСТАНОВОЧНЫЙ ТЕСТ (проверка H₀):")

n_permutations = 10000
budgets = df['budget'].values
revenues = df['revenue'].values

random_corrs = []
for i in range(n_permutations):
    shuffled = np.random.permutation(revenues)
    random_corrs.append(pd.Series(budgets).corr(pd.Series(shuffled)))

random_corrs = np.array(random_corrs)

p_value = np.mean(random_corrs >= actual_corr)
print(f"p-value = {p_value:.6f}")
print(f"(Вероятность получить r ≥ {actual_corr:.4f} если H₀ верна)")

print("\n" + "="*60)
print("ВЫВОД:")
print("="*60)

if p_value < 0.05:
    print("✓ Отвергается нулевая гипотеза H₀")
    print(f"  Есть статистически значимые доказательства")
    print(f"  в пользу положительной корреляции (p < 0.05)")
    print(f"  r = {actual_corr:.4f} ({strength.lower()} корреляция)")
else:
    print("✗ НЕ МОЖЕМ ОТВЕРГНУТЬ нулевую гипотезу H₀")
    print(f"  Недостаточно доказательств для принятия H₁")
    print(f"  Корреляция могла возникнуть случайно (p ≥ 0.05)")

print(f"\n" + "="*60)
print("ГИСТОГРАММА РАСПРЕДЕЛЕНИЯ КОЭФФИЦИЕНТОВ r")
print("="*60)

fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 6))

ax1.hist(random_corrs, bins=50, alpha=0.7, color='skyblue', edgecolor='black')
ax1.axvline(actual_corr, color='red', linewidth=3,
           label=f'Фактическая r = {actual_corr:.3f}')
ax1.axvline(0, color='gray', linestyle='--', linewidth=1, alpha=0.7,
           label='Нулевая корреляция (H₀)')
ax1.set_title('Распределение коэффициентов корреляции\nпри 10,000 случайных перестановок')
ax1.set_xlabel('Коэффициент корреляции r')
ax1.set_ylabel('Частота')
ax1.legend()
ax1.grid(True, alpha=0.3)

count_above = np.sum(random_corrs >= actual_corr)
ax1.text(0.05, 0.95, f'Случайных r ≥ фактической: {count_above} из {n_permutations}',
         transform=ax1.transAxes, fontsize=10,
         bbox=dict(boxstyle="round,pad=0.3", facecolor="white", alpha=0.8))

ax2.hist(random_corrs, bins=50, alpha=0.7, color='lightgreen', edgecolor='black',
        range=(-0.1, 0.1))
ax2.axvline(actual_corr, color='red', linewidth=3,
           label=f'Фактическая r = {actual_corr:.3f}')
ax2.axvline(0, color='gray', linestyle='--', linewidth=1, alpha=0.7)
ax2.set_title('Увеличенный вид (r от -0.1 до 0.1)\nОбласть нулевой гипотезы H₀')
ax2.set_xlabel('Коэффициент корреляции r')
ax2.set_ylabel('Частота')
ax2.legend()
ax2.grid(True, alpha=0.3)

percentile_95 = np.percentile(random_corrs, 95)
ax2.axvline(percentile_95, color='orange', linestyle=':', linewidth=2,
           label=f'95-й перцентиль = {percentile_95:.3f}')
ax2.legend()

plt.tight_layout()
plt.savefig('permutation_test_histogram.png', dpi=300, bbox_inches='tight')
plt.show()

print("\n" + "="*60)
print("СТАТИСТИКА ПЕРЕСТАНОВОЧНОГО ТЕСТА:")
print("="*60)
print(f"Среднее случайных r: {np.mean(random_corrs):.6f}")
print(f"Стандартное отклонение: {np.std(random_corrs):.6f}")
print(f"95-й перцентиль: {np.percentile(random_corrs, 95):.6f}")
print(f"99-й перцентиль: {np.percentile(random_corrs, 99):.6f}")
print(f"Фактический r = {actual_corr:.4f} превышает {percentile_95:.4f}")
print(f"  → {'Да, значимо!' if actual_corr > percentile_95 else 'Нет, не значимо'}")

print(f"\n✓ Гистограмма сохранена как 'permutation_test_histogram.png'")