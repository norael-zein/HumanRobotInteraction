import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt

#Read data
df = pd.read_csv("mood_detailed_summary.csv")
mean_cols = [col for col in df.columns if col.startswith("I feel") and "mean" in col]

df_long = df.melt(
    id_vars=["Which version of the robot were you interviewed by?", "Before/After"],
    value_vars=mean_cols,
    var_name="Mood",
    value_name="Mean rating"
)


df_long['Mood'] = df_long['Mood'].str.replace("I feel: ", "").str.replace(" mean", "").str.strip()

#Start with "before" then "after"
df_long['Before/After'] = pd.Categorical(df_long['Before/After'], categories=["Before", "After"], ordered=True)

#Create graph for each version
for version in df_long["Which version of the robot were you interviewed by?"].unique():
    plt.figure()
    ax = sns.barplot(
        data=df_long[df_long["Which version of the robot were you interviewed by?"] == version],
        x="Mood",
        y="Mean rating",
        hue="Before/After"
    )

    #Add mean values
    for container in ax.containers:
        for bar in container:
            height = bar.get_height()
            xpos = bar.get_x() + bar.get_width() * 1.0 
            ax.annotate(
                f"{height:.2f}",
                xy=(xpos, height),
                xytext=(0, 3),
                textcoords="offset points",
                ha='center',
                va='bottom'
            )

    plt.title(f"Mean Moods before and after interview with {version}")
    plt.xticks(rotation=45)
    plt.tight_layout()
    plt.show()
