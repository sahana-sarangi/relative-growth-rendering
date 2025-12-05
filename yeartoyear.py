import altair as alt
import json 

# ===================================================================
# 1. CONFIGURATION & DATA SOURCE
# ===================================================================

# !!! 1. CRITICAL: Replace this with your working GitHub RAW link (e.g., https://raw.githubusercontent.com/...) !!!
PUBLIC_DATA_URL = "https://media.githubusercontent.com/media/sahana-sarangi/relative-growth-rendering/refs/heads/main/final_combined_data.csv"

# --- Scale Definitions ---
min_tsne_x = -90.0  
max_tsne_x = 90.0  
min_tsne_y = -90.0  
max_tsne_y = 90.0  
max_growth = 0.6    

purple_center = 0.05
purple_range = 0.02
purple_min = purple_center - purple_range / 2
purple_max = purple_center + purple_range / 2

color_scale = alt.Scale(
    domain=[-0.2, purple_min, purple_max, max_growth],
    range=["#4575b4", "#762a83", "#762a83", "#d73027"]
)

# ===================================================================
# 2. SELECTION (DROPDOWN MENU)
# ===================================================================

# !!! 2. CRITICAL: Replace this list with your actual unique topic names !!!
MY_TOPIC_OPTIONS = ['All Topics', 'Topic 1', 'Topic 2', 'Topic 3', 'Topic 4', 'Topic 5'] 

topic_selection = alt.selection_point(
    fields=['TopicName'], 
    bind=alt.binding_select(
        name=' ', 
        options=MY_TOPIC_OPTIONS 
    ), 
    empty='all' 
)

# ===================================================================
# 3. CHART DEFINITION
# ===================================================================

base = alt.Chart(alt.Data(url=PUBLIC_DATA_URL)).properties(
    title=" " 
).interactive() # Enables Zoom and Pan

final_chart = base.mark_circle(size=25, opacity=0.9).encode(
    
    # Filter opacity controlled by the dropdown selection
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
# 4. GENERATE AND INJECT HTML
# ===================================================================

# Dump chart JSON string safely
chart_json = final_chart.to_json()

# Read the custom HTML template file
with open("template.html", 'r') as f:
    html_template = f.read()

# Placeholder string in template.html
PLACEHOLDER = "<!-- Chart embedding script will be added here -->"

# Inject the chart JSON into the template's placeholder script block
final_html = html_template.replace(
    PLACEHOLDER, 
    f"""
    <script>
      var spec = {chart_json};
      // Embed the spec into the #vis div. Controls go into #filter-controls.
      vegaEmbed('#vis', spec, {{
        actions: false, 
        mode: 'vega-lite',
        controls_div: '#filter-controls' 
      }});
    </script>
    """
)

# Write the final index.html file
with open("index.html", 'w') as f:
    f.write(final_html)