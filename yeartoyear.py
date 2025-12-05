import pandas as pd
import numpy as np
import altair as alt

alt.data_transformers.disable_max_rows()

def add_leading_zeroes(x):
    if pd.isna(x):
        x = 0
    return "{:02d}".format(int(x))

astro_url = "https://drive.google.com/uc?export=download&id=1hmZY1_fJ157l9VVV62ewg6NDCOU2WfUp"
tsne_url = "https://drive.google.com/uc?export:download&id=1hWBkhr2iQQm8hP3oa8kB_5Org40MND1s"
names_url = "https://drive.google.com/uc?export:download&id=1_SxyudGo4_zOa-pWvd3feXJjK_cELCYz"

data = pd.read_csv(astro_url, index_col=0)
data['years'] = data['years'].fillna(0)
data.years = data.years.astype(int)
data = data.rename(columns={"years": "Year"})

df = pd.read_csv(tsne_url, encoding="utf8")
df = df.rename(columns={
    "Topic Name (Post Forced)": "Cluster",
    "x": "TSNE-x",
    "y": "TSNE-y",
    "title": "AbstractTitle",
    "abstract": "Abstract"
})
df["Topic (Post Forced)"] = df["Topic (Post Forced)"].fillna(0).astype(int)
df = pd.merge(df, data, on=['AbstractTitle'], suffixes=("_df", None))
df = df.drop(columns=df.filter(regex="_df$").columns)
df['Index'] = np.arange(1, df.shape[0] + 1)
df["Cluster"] = df["Topic (Post Forced)"].apply(add_leading_zeroes)

bt60_names = pd.read_csv(names_url)
bt60_names = bt60_names.rename(columns={"title": "AbstractTitle"})
bt60_names["Topic (Post Forced)"] = bt60_names["Topic (Post Forced)"].fillna(0).astype(int)
df = pd.merge(
    df,
    bt60_names[["AbstractTitle", "GPT_Names", "Topic (Post Forced)"]],
    on=["AbstractTitle", "Topic (Post Forced)"],
    how="left"
)

df = df.rename(columns={"GPT_Names": "TopicName"})
df["TopicName"] = df["TopicName"].fillna("Topic " + df["Topic (Post Forced)"].astype(str))

df = df[
    ~df["TopicName"].str.strip().isin([
        "COVID-19 Impact on Radiation Oncology Practice",
        "Breast Cancer Radiotherapy Bolus Innovations",
        "Radioprotective Effects of Gut Microbiota-Derived Metabolites"
    ])
]

df["TopicName"] = df["TopicName"].apply(lambda x: x if len(x) <= 50 else x[:47] + "...")

topic_growth = (
    df.groupby(["TopicName", "Year"])
    .size()
    .reset_index(name="AbstractsPerYear")
)

def calc_year_to_year_growth(g):
    g = g.sort_values("Year")
    counts = g["AbstractsPerYear"].values
    if len(counts) < 2:
        return 0.0
    pct_changes = (counts[1:] - counts[:-1]) / counts[:-1]
    return np.mean(pct_changes)

yearly_growth = (
    topic_growth.groupby("TopicName")
    .apply(calc_year_to_year_growth)
    .reset_index(name="RelativeGrowthRate")
)

df = df.merge(yearly_growth, on="TopicName", how="left")
df["RelativeGrowthRate"] = df["RelativeGrowthRate"].fillna(0.0)

min_tsne_x = df["TSNE-x"].min()
max_tsne_x = df["TSNE-x"].max()
min_tsne_y = df["TSNE-y"].min()
max_tsne_y = df["TSNE-y"].max()

min_growth = df["RelativeGrowthRate"].min()
max_growth = df["RelativeGrowthRate"].max()

purple_center = 0.05
purple_range = 0.02
purple_min = purple_center - purple_range / 2
purple_max = purple_center + purple_range / 2

color_scale = alt.Scale(
    domain=[-0.2, purple_min, purple_max, max_growth],
    range=["#4575b4", "#762a83", "#762a83", "#d73027"]
)

filtered_df = df

final_chart = (
    alt.Chart(filtered_df)
    .mark_circle(size=25, opacity=0.9)
    .encode(
        x=alt.X(
            "TSNE-x:Q", 
            title="t-SNE x",
            scale=alt.Scale(domain=(min_tsne_x, max_tsne_x))
        ),
        y=alt.Y(
            "TSNE-y:Q", 
            title="t-SNE y",
            scale=alt.Scale(domain=(min_tsne_y, max_tsne_y))
        ),
        color=alt.Color(
            "RelativeGrowthRate:Q",
            scale=color_scale,
            title="Avg Year to Year Growth (% per year)",
            legend=alt.Legend(
                orient="right",
                titleFontSize=13,
                labelFontSize=11,
                labelLimit=250,
                format=".1%",
                gradientLength=200,
                direction="vertical",
                gradientThickness=20
            )
        ),
        tooltip=[
            alt.Tooltip("AbstractTitle:N", title="Abstract Title"),
            alt.Tooltip("TopicName:N", title="Topic Name"),
            alt.Tooltip("RelativeGrowthRate:Q", title="Avg. Year-to-Year Growth", format=".2%"),
            alt.Tooltip("Year:Q", title="Year")
        ],
    )
    .properties(title="Year To Year Relative Growth - t-SNE Map", width=700, height=1000)
    .configure_title(fontSize=18, anchor="start")
    .configure_axis(labelFontSize=12, titleFontSize=14, grid=True)
    .configure_view(strokeWidth=0)
)

final_chart.save("tsne_growth_map.html")
