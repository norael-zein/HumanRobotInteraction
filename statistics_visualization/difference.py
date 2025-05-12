import pandas as pd

#Read file 
df = pd.read_csv("mood_detailed_summary.csv")
df["group_id"] = df.groupby(["What is your gender?", "Which version of the robot were you interviewed by?", "Before/After"]).cumcount()
df_before = df[df["Before/After"] == "Before"].copy()
df_after = df[df["Before/After"] == "After"].copy()

merged = pd.merge(
    df_before,
    df_after,
    on=["What is your gender?", "Which version of the robot were you interviewed by?", "group_id"],
    suffixes=("_before", "_after")
)
mean_cols = [col for col in df.columns if "mean" in col]

#Calculate difference between mood after and before
for col in mean_cols:
    base = col.replace(" mean", "").strip()
    merged[f"{base}_diff"] = merged[f"{col}_after"] - merged[f"{col}_before"]


diff_cols = [col for col in merged.columns if col.endswith("_diff")]
result_df = merged[["Which version of the robot were you interviewed by?", "What is your gender?"] + diff_cols]
print(result_df)

#Save file
result_df.to_csv("emotion_differences.csv", index=False)
