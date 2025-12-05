import altair as alt
import json 
import pandas as pd 
import io 

# ===================================================================
# 1. CONFIGURATION & DATA SOURCE
# ===================================================================

# !!! CRITICAL: Use your confirmed working GitHub RAW link here !!!
PUBLIC_DATA_URL = "https://raw.githubusercontent.com/sahana-sarangi/relative-growth-rendering/main/final_combined_data.csv" 

# --- Dynamic Topic Extraction ---
try:
    # Load data from the public URL for topic list extraction
    data_response = pd.read_csv(PUBLIC_DATA_URL)
    unique_topics = data_response['TopicName'].unique().tolist()
    MY_TOPIC_OPTIONS = ['All Topics'] + sorted(unique_topics)
except Exception:
    # Fallback in case of data loading error
    MY_TOPIC_OPTIONS = ['All Topics', 'Data Load Error'] 
    
# --- Scale Definitions ---
min_tsne_x = -90.0  
max_tsne_x = 90.0  
min_tsne_y = -90.0  
max_tsne_y = 90.0  
max_growth = 0.6    

# Define the central, near-zero band (0.05 +/- 0.01)
center_growth = 0.05
band_range = 0.02
band_min = center_growth - (band_range / 2)
band_max = center_growth + (band_range / 2)


# ===================================================================
# 2. ACCESSIBLE COLOR SCALE (Orange to Blue, NO WHITE)
# ===================================================================

# Domain: [-0.2 (Low), band_min, band_max, max_growth (High)]
# Range: [Blue (Low), Dark Gray (Neutral Band Start), Dark Gray (Neutral Band End), Orange (High)]
color_scale = alt.Scale(
    domain=[-0.2, band_min, band_max, max_growth],
    # Uses a dark gray center for contrast instead of white
    range=["#1f78b4", "#4c4c4c", "#4c4c4c", "#ff7f00"] 
)

# ===================================================================
# 3. SELECTION & CHART DEFINITION 
# ===================================================================

topic_selection = alt.selection_point(
    fields=['TopicName'], 
    bind=alt.binding_select(
        options=MY_TOPIC_OPTIONS 
    ), 
    empty='all' 
)

# Data loading is correct; reloading the file should fix the breakage.
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
        scale=color_scale, # NEW ACCESSIBLE SCALE APPLIED HERE
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

chart_json = final_chart.to_json()

# This uses the template.html (which has the fixed layout CSS)
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