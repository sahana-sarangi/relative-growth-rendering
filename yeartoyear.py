
'''
import altair as alt
import pandas as pd

PUBLIC_DATA_URL = "https://media.githubusercontent.com/media/sahana-sarangi/relative-growth-rendering/refs/heads/main/final_combined_data.csv"

data_response = pd.read_csv(PUBLIC_DATA_URL)
unique_topics = data_response['TopicName'].unique().tolist()
MY_TOPIC_OPTIONS = ['All Topics'] + sorted(unique_topics)

min_tsne_x = -90.0
max_tsne_x = 90.0
min_tsne_y = -90.0
max_tsne_y = 90.0
max_growth = 0.4

purple_center = 0.05
purple_range = 0.02
purple_min = purple_center - purple_range / 2
purple_max = purple_center + purple_range / 2

color_scale = alt.Scale(
    domain=[-0.2, purple_min, purple_max, max_growth],
    range=["#4575B4", "#FFFFBF", "#FFFFBF", "#D73027"]
)

topic_selection = alt.selection_point(
    fields=['TopicName'],
    bind=alt.binding_select(options=MY_TOPIC_OPTIONS),
    empty='all'
)

controls_chart = alt.Chart(
    alt.Data(url=PUBLIC_DATA_URL)
).mark_text().add_params(
    topic_selection
).properties(
    width=1000,
    height=40
)

base = alt.Chart(
    alt.Data(url=PUBLIC_DATA_URL)
).interactive()

main_chart = base.mark_circle(size=25, opacity=1.0).encode(
    opacity=alt.condition(topic_selection, alt.value(1.0), alt.value(0.0)),
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
            format=".1%",
            gradientLength=200,
            gradientThickness=20
        )
    ),
    tooltip=[
        alt.Tooltip("AbstractTitle:N", title="Abstract Title"),
        alt.Tooltip("TopicName:N", title="Topic Name"),
        alt.Tooltip("RelativeGrowthRate:Q", title="Avg. Year-to-Year Growth", format=".2%"),
        alt.Tooltip("Year:Q", title="Year")
    ]
).properties(
    width=1000,
    height=1000
)

final_chart = alt.vconcat(
    controls_chart,
    main_chart,
    spacing=10
).configure_view(
    stroke=None
)

chart_json = final_chart.to_json()

with open("template.html", "r") as f:
    html_template = f.read()

PLACEHOLDER = "<!-- Chart embedding script will be added here -->"

final_html = html_template.replace(
    PLACEHOLDER,
    f"""
    <script>
      var spec = {chart_json};
      vegaEmbed('#vis', spec, {{
        actions: false,
        mode: 'vega-lite'
      }});
    </script>
    """
)

with open("index.html", "w") as f:
    f.write(final_html)
'''
'''
import altair as alt
import pandas as pd

# CSV URL
PUBLIC_DATA_URL = "https://media.githubusercontent.com/media/sahana-sarangi/relative-growth-rendering/refs/heads/main/final_combined_data.csv"

# Load CSV in Python only to get the dynamic dropdown options
df = pd.read_csv(PUBLIC_DATA_URL)
MY_TOPIC_OPTIONS = ['All Topics'] + sorted(df['TopicName'].unique())

# t-SNE and growth bounds
min_tsne_x, max_tsne_x = -90.0, 90.0
min_tsne_y, max_tsne_y = -90.0, 90.0
max_growth = 0.4

# Neutral purple color range
purple_center, purple_range = 0.05, 0.02
purple_min = purple_center - purple_range / 2
purple_max = purple_center + purple_range / 2

color_scale = alt.Scale(
    domain=[-0.2, purple_min, purple_max, max_growth],
    range=["#4575B4", "#FFFFBF", "#FFFFBF", "#D73027"]
)

# Dynamic dropdown selection
topic_selection = alt.selection_point(
    fields=['TopicName'],
    bind=alt.binding_select(options=MY_TOPIC_OPTIONS),
    empty='all',
    name='Select'
)

# Base chart using URL (data not embedded, avoids 5000-row limit)
base = alt.Chart(PUBLIC_DATA_URL).interactive()

# Main scatter chart
main_chart = base.mark_circle(size=25).encode(
    opacity=alt.condition(topic_selection, alt.value(1.0), alt.value(0.1)),
    x=alt.X("TSNE-x:Q", scale=alt.Scale(domain=(min_tsne_x, max_tsne_x)), title="t-SNE x"),
    y=alt.Y("TSNE-y:Q", scale=alt.Scale(domain=(min_tsne_y, max_tsne_y)), title="t-SNE y"),
    color=alt.Color(
        "RelativeGrowthRate:Q",
        scale=color_scale,
        title="Avg Year to Year Growth (% per year)",
        legend=alt.Legend(orient="right", format=".1%", gradientLength=200, gradientThickness=20)
    ),
    tooltip=[
        alt.Tooltip("AbstractTitle:N", title="Abstract Title"),
        alt.Tooltip("TopicName:N", title="Topic Name"),
        alt.Tooltip("RelativeGrowthRate:Q", title="Avg. Year-to-Year Growth", format=".2%"),
        alt.Tooltip("Year:Q", title="Year")
    ]
).add_params(topic_selection).properties(width=1000, height=1000)

# Chart JSON
chart_json = main_chart.to_json()

# Load HTML template
with open("template.html", "r") as f:
    html_template = f.read()

PLACEHOLDER = "<!-- Chart embedding script will be added here -->"

# Inject chart JSON into HTML
final_html = html_template.replace(
    PLACEHOLDER,
    f"""
    <script>
      var spec = {chart_json};
      vegaEmbed('#vis', spec, {{
        actions: false,
        mode: 'vega-lite',
        controls_div: '#filter-controls'
      }});
    </script>
    """
)

# Write final HTML
with open("index.html", "w") as f:
    f.write(final_html)
'''

import altair as alt
import pandas as pd

# -----------------------------
# Data source
# -----------------------------
PUBLIC_DATA_URL = (
    "https://media.githubusercontent.com/media/"
    "sahana-sarangi/relative-growth-rendering/"
    "refs/heads/main/final_combined_data.csv"
)

# Load once in Python to extract topics
df = pd.read_csv(PUBLIC_DATA_URL)
topics = sorted(df["TopicName"].dropna().unique().tolist())

# IMPORTANT: None represents "All Topics"
DROPDOWN_OPTIONS = [None] + topics
DROPDOWN_LABELS = ["All Topics"] + topics

# -----------------------------
# Selection
# -----------------------------
topic_selection = alt.selection_point(
    fields=["TopicName"],
    bind=alt.binding_select(
        options=DROPDOWN_OPTIONS,
        labels=DROPDOWN_LABELS
    ),
    empty="all",
    name="Select"
)

# -----------------------------
# Color scale
# -----------------------------
color_scale = alt.Scale(
    domain=[-0.2, 0.04, 0.06, 0.4],
    range=["#4575B4", "#FFFFBF", "#FFFFBF", "#D73027"],
)

# -----------------------------
# Base chart
# -----------------------------
base = alt.Chart(PUBLIC_DATA_URL).interactive()

# -----------------------------
# Main scatter plot
# -----------------------------
main_chart = (
    base.mark_circle(size=25)
    .encode(
        x=alt.X("TSNE-x:Q", scale=alt.Scale(domain=(-90, 90)), title="t-SNE x"),
        y=alt.Y("TSNE-y:Q", scale=alt.Scale(domain=(-90, 90)), title="t-SNE y"),
        color=alt.Color(
            "RelativeGrowthRate:Q",
            scale=color_scale,
            title="Avg Year to Year Growth (% per year)",
            legend=alt.Legend(
                orient="right",
                format=".0%"
            ),
        ),
        opacity=alt.condition(
            topic_selection,
            alt.value(1.0),
            alt.value(0.1),
        ),
        tooltip=[
            alt.Tooltip("AbstractTitle:N", title="Abstract Title"),
            alt.Tooltip("TopicName:N", title="Topic Name"),
            alt.Tooltip(
                "RelativeGrowthRate:Q",
                title="Avg. Year-to-Year Growth",
                format=".2%",
            ),
            alt.Tooltip("Year:Q", title="Year"),
        ],
    )
    .add_params(topic_selection)
    .properties(width=1000, height=1000)
)

# -----------------------------
# Export JSON
# -----------------------------
chart_json = main_chart.to_json()

# -----------------------------
# Inject into HTML
# -----------------------------
with open("template.html", "r") as f:
    html_template = f.read()

PLACEHOLDER = "<!-- Chart embedding script will be added here -->"

final_html = html_template.replace(
    PLACEHOLDER,
    f"""
    <script>
      var spec = {chart_json};
      vegaEmbed('#vis', spec, {{
        actions: false,
        mode: 'vega-lite',
        controls_div: '#filter-controls'
      }});
    </script>
    """
)

with open("index.html", "w") as f:
    f.write(final_html)
