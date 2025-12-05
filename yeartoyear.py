import altair as alt
import json 
import pandas as pd
import io 

PUBLIC_DATA_URL = "https://media.githubusercontent.com/media/sahana-sarangi/relative-growth-rendering/refs/heads/main/final_combined_data.csv"

# --- Dynamic Topic Extraction ---
try:
    data_response = pd.read_csv(PUBLIC_DATA_URL)
    unique_topics = data_response['TopicName'].unique().tolist()
    MY_TOPIC_OPTIONS = ['All Topics'] + sorted(unique_topics)
except Exception:
    MY_TOPIC_OPTIONS = ['All Topics', 'Data Load Error'] 
    
# --- Scale Definitions (max_growth updated) ---
min_tsne_x = -90.0  
max_tsne_x = 90.0  
min_tsne_y = -90.0  
max_tsne_y = 90.0  
max_growth = 0.4    # CHANGED from 0.6 to 0.4 (40%) as requested

purple_center = 0.05
purple_range = 0.02
purple_min = purple_center - purple_range / 2
purple_max = purple_center + purple_range / 2

# CRITICAL UPDATE: 
# Changed color range to Dark Orange (high) -> Brown (neutral) -> Deep Cyan (low).
# Hex codes used: Deep Cyan (#008b8b), Brown (#a0522d), Dark Orange (#cc5500).
color_scale = alt.Scale(
    domain=[-0.2, purple_min, purple_max, max_growth],
    # Range is Deep Cyan (low), Brown (neutral low), Brown (neutral high), Dark Orange (high)
    range=["#008b8b", "#a0522d", "#a0522d", "#cc5500"]
)

# ===================================================================
# 2. SELECTION (DROPDOWN MENU)
# ===================================================================

topic_selection = alt.selection_point(
    fields=['TopicName'], 
    bind=alt.binding_select(
        # CRITICAL CHANGE: name property removed 
        options=MY_TOPIC_OPTIONS 
    ), 
    empty='all' 
)

# ===================================================================
# 3. CHART DEFINITION (Unchanged)
# ===================================================================

base = alt.Chart(alt.Data(url=PUBLIC_DATA_URL)).properties(
    title=" " 
).interactive()

final_chart = base.mark_circle(size=25, opacity=0.9).encode(
    
    opacity=alt.condition(topic_selection, alt.value(0.9), alt.value(0.1)),
    
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
    ]
).add_params(
    topic_selection 
).properties(
    width=1000, 
    height=1000
).configure_title(
    fontSize=18, anchor="start"
)

# ===================================================================
# 4. GENERATE AND INJECT HTML (Unchanged)
# ===================================================================

chart_json = final_chart.to_json()

with open("template.html", 'r') as f:
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

with open("index.html", 'w') as f:
    f.write(final_html)