import pandas as pd
import numpy as np
from scipy.stats import ttest_ind, shapiro, levene, mannwhitneyu

#Read data
df = pd.read_csv("data.csv", sep=';')

df.rename(columns={" Subject ID": "Subject ID"}, inplace=True)
df["Subject ID"] = df["Subject ID"].str.strip()
df["Base ID"] = df["Subject ID"].str.replace(r"_before|_after", "", regex=True)
df["Before/After"] = df["Before/After"].str.strip()

before_df = df[df["Before/After"] == "Before"].set_index("Base ID")
after_df = df[df["Before/After"] == "After"].set_index("Base ID")

common_ids = before_df.index.intersection(after_df.index)
before_df = before_df.loc[common_ids]
after_df = after_df.loc[common_ids]

mood_cols = [col for col in df.columns if col.startswith("I feel:")]

#Calculate difference
diff_df = after_df[mood_cols] - before_df[mood_cols]
diff_df["Version"] = before_df["Which version of the robot were you interviewed by?"]

#Cohen function
def cohen_d(x, y):
    #Parametric effect size
    nx = len(x)
    ny = len(y)
    pooled_std = np.sqrt(((nx - 1) * x.std(ddof=1)**2 + (ny - 1) * y.std(ddof=1)**2) / (nx + ny - 2))
    return (x.mean() - y.mean()) / pooled_std

def cliffs_delta(x, y):
    #Non-parametric effect-size
    x = np.array(x)
    y = np.array(y)
    nx = len(x)
    ny = len(y)
    greater = sum(xi > yi for xi in x for yi in y)
    less = sum(xi < yi for xi in x for yi in y)
    return (greater - less) / (nx * ny)

#Run tests 
test_results = []

for mood_col in mood_cols:
    mood = mood_col.replace("I feel: ", "").strip()
    group1 = diff_df[diff_df["Version"] == "Version 1"][mood_col].dropna()
    group2 = diff_df[diff_df["Version"] == "Version 2"][mood_col].dropna()

    if len(group1) == 0 or len(group2) == 0:
        continue

    shapiro_1 = shapiro(group1)
    shapiro_2 = shapiro(group2)
    levene_p = levene(group1, group2).pvalue

    if shapiro_1.pvalue > 0.05 and shapiro_2.pvalue > 0.05 and levene_p > 0.05:
        stat, p = ttest_ind(group1, group2)
        test_used = "T-test"
        d = cohen_d(group1, group2)
    else:
        stat, p = mannwhitneyu(group1, group2)
        test_used = "Mann-Whitney"
        d = cliffs_delta(group1, group2)

    test_results.append({
        "Mood": mood,
        "Mean Change V1": group1.mean(),
        "Mean Change V2": group2.mean(),
        "Shapiro V1 p": round(shapiro_1.pvalue, 3),
        "Shapiro V2 p": round(shapiro_2.pvalue, 3),
        "Levene p": round(levene_p, 3),
        "Test Used": test_used,
        "Statistic": round(stat, 3),
        "p-value": round(p, 3),
        "Cohen's d/Cliff's delta": round(d, 3) #if not np.isnan(d) else "N/A"
    })

#Results
results_df = pd.DataFrame(test_results)
print(results_df)
results_df.to_excel("results_table.xlsx", index=False)
