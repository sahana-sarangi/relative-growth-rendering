

import altair as alt
import pandas as pd

# Data source
PUBLIC_DATA_URL = "https://media.githubusercontent.com/media/sahana-sarangi/relative-growth-rendering/refs/heads/main/final_combined_data.csv"

# Load data to get dropdown options
df = pd.read_csv(PUBLIC_DATA_URL)
topics = sorted(df["TopicName"].dropna().unique().tolist())

DROPDOWN_OPTIONS = [None] + topics
DROPDOWN_LABELS = ["All Topics"] + topics

# Setup Selection
topic_selection = alt.selection_point(
    fields=['TopicName'],
    bind=alt.binding_select(
        options=DROPDOWN_OPTIONS,
        labels=DROPDOWN_LABELS,
        name=" " 
    ),
    empty="all",
    name="Select"
)

# Color Scale
color_scale = alt.Scale(
    domain=[-0.2, 0.04, 0.06, 0.4],
    range=["#4575B4", "#FFFFBF", "#FFFFBF", "#D73027"],
)

# Create Chart
main_chart = (
    alt.Chart(PUBLIC_DATA_URL)
    .mark_circle(size=25)
    .encode(
        x=alt.X("TSNE-x:Q", scale=alt.Scale(domain=(-90, 90)), title="t-SNE x"),
        y=alt.Y("TSNE-y:Q", scale=alt.Scale(domain=(-90, 90)), title="t-SNE y"),
        color=alt.Color(
            "RelativeGrowthRate:Q",
            scale=color_scale,
            title="Growth Rate",
            legend=alt.Legend(
                orient="right", 
                format=".0%",
                offset=30, # Extra push to keep away from axis labels
                titleFontSize=13,
                labelFontSize=12
            )
        ),
        opacity=alt.condition(topic_selection, alt.value(1.0), alt.value(0.1)),
        tooltip=[
            alt.Tooltip("AbstractTitle:N", title="Abstract Title"),
            alt.Tooltip("TopicName:N", title="Topic Name"),
            alt.Tooltip("RelativeGrowthRate:Q", title="Growth", format=".2%"),
        ],
    )
    .add_params(topic_selection)
    .properties(width=850, height=750) # Fixed width helps prevent legend clipping
    .interactive()
    .configure(padding={"left": 50, "top": 50, "right": 150, "bottom": 50}) # Massive right padding
    .configure_view(stroke=None)
)

chart_json = main_chart.to_json()

# Process HTML
with open("template.html", "r") as f:
    html_template = f.read()

# Using a very simple string replacement
final_html = html_template.replace("INSERT_SPEC_VARIABLE_HERE", f"var spec = {chart_json};")

with open("index.html", "w") as f:
    f.write(final_html)
