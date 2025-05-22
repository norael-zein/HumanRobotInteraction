import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
"""
Correlations between changes in emotional state within each group
"""
#Load data
df = pd.read_csv("data.csv", sep=';')
df.rename(columns={" Subject ID": "Subject ID"}, inplace=True)
df["Subject ID"] = df["Subject ID"].str.strip()
df["Base ID"] = df["Subject ID"].str.replace(r"_before|_after", "", regex=True)
df["Before/After"] = df["Before/After"].str.strip()

#Separate before and after
before_df = df[df["Before/After"] == "Before"].set_index("Base ID")
after_df = df[df["Before/After"] == "After"].set_index("Base ID")

#Identify participants with both before and after
common_ids = before_df.index.intersection(after_df.index)
before_df = before_df.loc[common_ids]
after_df = after_df.loc[common_ids]

#Identify mood columns
mood_cols = [col for col in df.columns if col.startswith("I feel:")]

#Calculate mood change
mood_change_df = after_df[mood_cols] - before_df[mood_cols]
mood_change_df["Version"] = before_df["Which version of the robot were you interviewed by?"]

#Plot correlation matrices for Version 1 and Version 2
for version in ["Version 1", "Version 2"]:
    version_changes = mood_change_df[mood_change_df["Version"] == version][mood_cols]
    corr_matrix = version_changes.corr()

    plt.figure(figsize=(10, 8))
    sns.heatmap(corr_matrix, annot=True, cmap="coolwarm", fmt=".2f")
    plt.title(f"Correlation of Changes in Emotional state after interview — {version}")
    plt.xticks(rotation=45, ha='right')
    plt.yticks(rotation=0)
    plt.tight_layout()
    filename = f"correlation_{version}.png".replace(" ", "_")
    plt.savefig(filename)
    plt.show()