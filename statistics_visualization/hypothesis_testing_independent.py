""""
We are here looking for: Is the difference in group average moods significant
For example, is this statistically significant: “Is the average change in mood (e.g., Excited) different between people who interacted with Robot Version 1 and those who interacted with Version 2?
"""

import pandas as pd
from scipy.stats import ttest_ind, shapiro, levene, mannwhitneyu

df = pd.read_csv("data.csv", sep=';')
df.rename(columns={" Subject ID": "Subject ID"}, inplace=True)

#Clean and prepare base IDs
df["Subject ID"] = df["Subject ID"].str.strip()
df["Base ID"] = df["Subject ID"].str.replace(r"_before|_after", "", regex=True)
df["Before/After"] = df["Before/After"].str.strip()

#Separate before and after
before_df = df[df["Before/After"] == "Before"].set_index("Base ID")
after_df = df[df["Before/After"] == "After"].set_index("Base ID")

#Match participants who completed both before and after
common_ids = before_df.index.intersection(after_df.index)
before_df = before_df.loc[common_ids]
after_df = after_df.loc[common_ids]

#Identify mood-related columns
mood_cols = [col for col in df.columns if col.startswith("I feel:")]

#Calculate mood change (after - before)
diff_df = after_df[mood_cols] - before_df[mood_cols]
diff_df["Version"] = before_df["Which version of the robot were you interviewed by?"]

# Perform t-tests with assumption checks per mood
from scipy.stats import ttest_ind, shapiro, levene, mannwhitneyu

test_results = []

for mood_col in mood_cols:
    mood = mood_col.replace("I feel: ", "").strip()
    group1 = diff_df[diff_df["Version"] == "Version 1"][mood_col].dropna()
    group2 = diff_df[diff_df["Version"] == "Version 2"][mood_col].dropna()

    if len(group1) == 0 or len(group2) == 0:
        continue

    #Normality tests
    shapiro_1 = shapiro(group1)
    shapiro_2 = shapiro(group2)

    #Homogeneity of variances
    levene_p = levene(group1, group2).pvalue

    #Choose appropriate test
    if shapiro_1.pvalue > 0.05 and shapiro_2.pvalue > 0.05 and levene_p > 0.05:
        stat, p = ttest_ind(group1, group2)
        test_used = "T-test"
    else:
        stat, p = mannwhitneyu(group1, group2)
        test_used = "Mann-Whitney"

    test_results.append({
        "Mood": mood,
        "Mean Change V1": group1.mean(),
        "Mean Change V2": group2.mean(),
        "Shapiro V1 p": round(shapiro_1.pvalue, 3),
        "Shapiro V2 p": round(shapiro_2.pvalue, 3),
        "Levene p": round(levene_p, 3),
        "Test Used": test_used,
        "Statistic": round(stat, 3),
        "p-value": round(p, 3)
    })

results_df = pd.DataFrame(test_results)

print(results_df)