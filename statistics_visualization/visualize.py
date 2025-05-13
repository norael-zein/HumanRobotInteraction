import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt

#Read data
df = pd.read_csv("data.csv", sep=';')
df["Subject ID"] = df[" Subject ID"].str.strip()
df["Base ID"] = df["Subject ID"].str.replace(r"_before|_after", "", regex=True)
df["Before/After"] = df["Before/After"].str.strip()

#Separate before and after
before = df[df["Before/After"] == "Before"].set_index("Base ID")
after = df[df["Before/After"] == "After"].set_index("Base ID")
common_ids = before.index.intersection(after.index)
before = before.loc[common_ids]
after = after.loc[common_ids]

#Calculate changes per subject
mood_cols = [col for col in df.columns if col.startswith("I feel:")]
change = after[mood_cols] - before[mood_cols]
change["Version"] = before["Which version of the robot were you interviewed by?"]

df_long = change.reset_index().melt(
    id_vars=["Base ID", "Version"],
    value_vars=mood_cols,
    var_name="Mood",
    value_name="Mood Change"
)
df_long["Mood"] = df_long["Mood"].str.replace("I feel: ", "").str.strip()

for version in df_long["Version"].dropna().unique():
    plt.figure(figsize=(10, 6))
    ax = sns.barplot(
        data=df_long[df_long["Version"] == version],
        x="Mood",
        y="Mood Change",
        estimator="mean",
        ci=None
    )

    for bar in ax.patches:
        height = bar.get_height()
        ax.annotate(f"{height:.2f}", xy=(bar.get_x() + bar.get_width() / 2, height),
                    ha='center', va='bottom' if height > 0 else 'top')

    plt.title(f"Average Mood Change After Interview — {version}")
    plt.xticks(rotation=45)
    plt.axhline(0, color='black', linestyle='--')
    plt.tight_layout()
    plt.show()
