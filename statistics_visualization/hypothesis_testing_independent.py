###Independent Samples T-Test###

""""
We are here looking for: Is the difference in group average moods significant
For example, is this statistically significant: “Is the average change in mood (e.g., Excited) different between people who interacted with Robot Version 1 and those who interacted with Version 2?
"""
import pandas as pd
from scipy.stats import ttest_ind, shapiro, levene, mannwhitneyu

#Read data
df = pd.read_csv("emotion_differences.csv")
mood_cols = [col for col in df.columns if col.endswith("_diff")]

#Results
results = []

#Loop over all moods
for mood_col in mood_cols:
    mood = mood_col.replace("I feel: ", "").replace("_diff", "").strip()
    groupA = df[df["Which version of the robot were you interviewed by?"] == "Version 1"][mood_col].dropna()
    groupB = df[df["Which version of the robot were you interviewed by?"] == "Version 2"][mood_col].dropna()

    #If any group is empty
    if len(groupA) == 0 or len(groupB) == 0:
        continue

    #Check that we do not have any constant data
    if groupA.nunique() <= 1 or groupB.nunique() <= 1:
        shapiro_pA = shapiro_pB = 0.0
        levene_p = 0.0
        test_name = "N/A (constant values)"
        stat, p_val = 0.0, 1.0
    else:
        #Nomality values (Shapiro-Wilk test)
        shapiro_A = shapiro(groupA)
        shapiro_B = shapiro(groupB)
        #Homogenity of variance (Levene's test)
        levene_test = levene(groupA, groupB)

        shapiro_pA = shapiro_A.pvalue
        shapiro_pB = shapiro_B.pvalue
        levene_p = levene_test.pvalue

        #If both groups are normal (p>0.5) and variances are equal, proceed with t-test
        if shapiro_pA > 0.05 and shapiro_pB > 0.05 and levene_p > 0.05:
            test_name = "T-test"
            stat, p_val = ttest_ind(groupA, groupB)
        else:
            test_name = "Mann-Whitney"
            stat, p_val = mannwhitneyu(groupA, groupB)

    results.append({
        "Mood": mood,
        "Shapiro V1 p": round(shapiro_pA, 3),
        "Shapiro V2 p": round(shapiro_pB, 3),
        "Levene p": round(levene_p, 3),
        "Test": test_name,
        "Stat": round(stat, 3),
        "p-value": round(p_val, 3)
    })

results_df = pd.DataFrame(results)

print("\nSignificant differences (p < 0.05):")
print(results_df[results_df["p-value"] < 0.05])
print("\nInsignificant differences (p > 0.05):")
print(results_df[results_df["p-value"]> 0.5])
