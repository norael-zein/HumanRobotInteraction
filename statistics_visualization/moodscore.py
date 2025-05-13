import pandas as pd
import numpy as np

# Load and prepare data
df = pd.read_csv("data.csv", sep=';')
df.rename(columns={" Subject ID": "Subject ID"}, inplace=True)
df["Subject ID"] = df["Subject ID"].str.strip()
df["Base ID"] = df["Subject ID"].str.replace(r"_before|_after", "", regex=True)
df["Before/After"] = df["Before/After"].str.strip()

# Separate before and after
before_df = df[df["Before/After"] == "Before"].set_index("Base ID")
after_df = df[df["Before/After"] == "After"].set_index("Base ID")
common_ids = before_df.index.intersection(after_df.index)
before_df = before_df.loc[common_ids]
after_df = after_df.loc[common_ids]

# Identify mood columns
mood_cols = [col for col in df.columns if col.startswith("I feel:")]

# Calculate mood change
mood_change_df = after_df[mood_cols] - before_df[mood_cols]
mood_change_df["Version"] = before_df["Which version of the robot were you interviewed by?"]

# Define Cohen's d function
def cohen_d(x, y):
    nx = len(x)
    ny = len(y)
    pooled_std = np.sqrt(((nx-1)*x.std(ddof=1)**2 + (ny-1)*y.std(ddof=1)**2) / (nx + ny - 2))
    return (x.mean() - y.mean()) / pooled_std

# Compute effect size per mood
results = []

for mood_col in mood_cols:
    mood = mood_col.replace("I feel: ", "").strip()
    group1 = mood_change_df[mood_col][mood_change_df["Version"] == "Version 1"].dropna()
    group2 = mood_change_df[mood_col][mood_change_df["Version"] == "Version 2"].dropna()
    
    if len(group1) > 1 and len(group2) > 1:
        mean_diff = group1.mean() - group2.mean()
        effect_size = cohen_d(group1, group2)
    else:
        mean_diff = "N/A"
        effect_size = "N/A"
    
    results.append({
        "Mood": mood,
        "Mean Change V1": round(group1.mean(), 3) if not group1.empty else "N/A",
        "Mean Change V2": round(group2.mean(), 3) if not group2.empty else "N/A",
        "Mean Difference (V1 - V2)": round(mean_diff, 3) if mean_diff != "N/A" else "N/A",
        "Cohen's d": round(effect_size, 3) if effect_size != "N/A" else "N/A"
    })

results_df = pd.DataFrame(results)
print(results_df)