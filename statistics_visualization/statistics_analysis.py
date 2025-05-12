import pandas as pd

df = pd.read_csv("data.csv", delimiter=';')

mood_cols = [col for col in df.columns if col.startswith("I feel")]
group_keys = ["Which version of the robot were you interviewed by?", "Before/After", "What is your gender?"]

#Gender
grouped_gender_stats = df.groupby(group_keys)[mood_cols].describe().reset_index()
grouped_gender_stats.columns = [' '.join(col).strip() if isinstance(col, tuple) else col for col in grouped_gender_stats.columns]

#All 
group_keys_all = ["Which version of the robot were you interviewed by?", "Before/After"]
grouped_all_stats = df.groupby(group_keys_all)[mood_cols].describe().reset_index()
grouped_all_stats['What is your gender?'] = 'All'  
grouped_all_stats.columns = [' '.join(col).strip() if isinstance(col, tuple) else col for col in grouped_all_stats.columns]

#Combine dataframes
final_stats = pd.concat([grouped_gender_stats, grouped_all_stats], ignore_index=True)

#Save to CSV
final_stats.to_csv("mood_detailed_summary.csv", index=False)
