###Paired Samples T-Test

import pandas as pd
from scipy.stats import ttest_rel, shapiro
from scipy.stats import wilcoxon

""" 
We are here looking for: If there is a statistically significant change in a Person's mood before vs after the conversation
For example:  if there's a statistically significant change in Person 1s enthusiasm, before vs. after the conversation.
"""

df = pd.read_csv("data.csv", sep=';')

grouped_results = []

#Loop over each robot version
for version in df["Which version of the robot were you interviewed by?"].dropna().unique():
    version_df = df[df["Which version of the robot were you interviewed by?"] == version].copy()

    version_df["Subject ID"] = version_df[" Subject ID"].str.strip()
    version_df["Base ID"] = version_df["Subject ID"].str.replace(r"_before|_after", "", regex=True)
    version_df["Before/After"] = version_df["Before/After"].str.strip()

    before_df = version_df[version_df["Before/After"] == "Before"].set_index("Base ID")
    after_df = version_df[version_df["Before/After"] == "After"].set_index("Base ID")
    common_ids = before_df.index.intersection(after_df.index)
    before_df = before_df.loc[common_ids]
    after_df = after_df.loc[common_ids]

    #Mood columns
    mood_cols = [col for col in version_df.columns if col.startswith("I feel:")]

    #Run paired test for each mood
    for mood_col in mood_cols:
        mood = mood_col.replace("I feel: ", "").strip()
        before = before_df[mood_col]
        after = after_df[mood_col]
        diff = after - before

        if diff.nunique() <= 1:
            grouped_results.append({
                "Version": version,
                "Mood": mood,
                "Shapiro-Wilk p": "N/A",
                "Test": "No variation",
                "Statistic": "N/A",
                "p-value": "N/A"
            })
            continue

        shapiro_p = shapiro(diff).pvalue

        if shapiro_p > 0.05:
            test = "Paired t-test"
            stat, p = ttest_rel(after, before)
        else:
            test = "Wilcoxon"
            stat, p = wilcoxon(after, before)

        grouped_results.append({
            "Version": version,
            "Mood": mood,
            "Shapiro-Wilk p": round(shapiro_p, 3),
            "Test": test,
            "Statistic": round(stat, 3),
            "p-value": round(p, 3)
        })

grouped_df = pd.DataFrame(grouped_results)
print(grouped_df)

