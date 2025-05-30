import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np

#Read data
df = pd.read_csv("data.csv", sep=';')
df.rename(columns={" Subject ID": "Subject ID"}, inplace=True)
df["Subject ID"] = df["Subject ID"].str.strip()
df["Base ID"] = df["Subject ID"].str.replace(r"_before|_after", "", regex=True)
df["Before/After"] = df["Before/After"].str.strip()

before = df[df["Before/After"] == "Before"].set_index("Base ID")
after = df[df["Before/After"] == "After"].set_index("Base ID")
common_ids = before.index.intersection(after.index)
before = before.loc[common_ids]
after = after.loc[common_ids]

#Select emotional states
mood_cols = [col for col in df.columns if col.startswith("I feel:")]

#Calculate difference
change = after[mood_cols] - before[mood_cols]
change["Version"] = before["Which version of the robot were you interviewed by?"]
change["Gender"] = before["What is your gender?"]
change = change.reset_index()

df_long_gender = change.melt(
    id_vars=["Base ID", "Version", "Gender"],
    value_vars=mood_cols,
    var_name="Emotional state",
    value_name="Emotional state Change"
)
df_long_gender["Emotional state"] = df_long_gender["Emotional state"].str.replace("I feel: ", "").str.strip()

def plot_mood_change_by_gender(data, version, gender):
    subset = data[(data["Version"] == version) & (data["Gender"] == gender)]
    if subset.empty:
        return
    plt.figure(figsize=(10, 6))
    ax = sns.barplot(
        data=subset,
        x="Emotional state",
        y="Emotional state Change",
        estimator=np.mean,
        ci=None
    )
    plt.axhline(0, color='black', linestyle='--')
    plt.title(f"Average Change in Emotional state — {gender} — {version}")
    plt.ylabel("Mean Change Emotional state (After - Before)")
    plt.xticks(rotation=45, ha='right')
    for bar in ax.patches:
        height = bar.get_height()
        ax.text(bar.get_x() + bar.get_width() / 2, height,
                f"{height:.2f}", ha='center', va='bottom' if height > 0 else 'top')
    plt.tight_layout()
    filename = f"emotional_state_change_{version}_{gender}.png".replace(" ", "_")
    plt.savefig(filename)
    plt.show()

#Graphs
for version in df_long_gender["Version"].dropna().unique():
    for gender in df_long_gender["Gender"].dropna().unique():
        plot_mood_change_by_gender(df_long_gender, version, gender)
