import altair as alt
import json 
import pandas as pd 
import io 

# ===================================================================
# 1. CONFIGURATION & DATA SOURCE
# ===================================================================

# NOTE: Switched to a stable GitHub RAW link for reliable Altair data loading, 
# as the previous Dropbox sharing link often fails to load raw CSV data.
PUBLIC_DATA_URL = "https://raw.githubusercontent.com/sahana-sarangi/relative-growth-rendering/main/final_combined_data.csv" 

# --- Dynamic Topic Extraction ---
# This part is necessary to populate the new manual dropdown in the HTML
try:
    # Load data from the public URL for topic list extraction
    data_response = pd.read_csv(PUBLIC_DATA_URL)
    unique_topics = data_response['TopicName'].unique().tolist()
    MY_TOPIC_OPTIONS = ['All Topics'] + sorted(unique_topics)
except Exception:
    # Fallback in case of data loading error
    MY_TOPIC_OPTIONS = ['All Topics', 'Data Load Error'] 
    
# --- Scale Definitions (Using your provided values) ---
min_tsne_x = -15.0  
max_tsne_x = 15.0   
min_tsne_y = -15.0  
max_tsne_y = 15.0   
max_growth = 0.6    

purple_center = 0.05
purple_range = 0.02
purple_min = purple_center - purple_range / 2
purple_max = purple_center + purple_range / 2

# ===================================================================
# 2. COLOR SCALE
# ===================================================================

# Using your custom color scale configuration
color_scale = alt.Scale(
    domain=[-0.2, purple_min, purple_max, max_growth],
    range=["#4575b4", "#762a83", "#762a83", "#d73027"]
)

# ===================================================================
# 3. SELECTION & CHART DEFINITION 
# ===================================================================

# Define a simple parameter (signal) for the filter. This will be controlled manually by JavaScript.
topic_param = alt.param(name='topic_selection', value='All Topics')

base = alt.Chart(alt.Data(url=PUBLIC_DATA_URL)).properties(
    title=" " 
).interactive()

final_chart = base.mark_circle(size=25, opacity=0.9).encode(
    
    # Conditional opacity based on the parameter value
    opacity=alt.condition(
        (topic_param == 'All Topics') | (alt.datum.TopicName == topic_param), 
        alt.value(0.9), 
        alt.value(0.1)
    ),
    
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
    topic_param # Attach the parameter so it can be controlled by the Vega View API
).properties(
    title="Year To Year Relative Growth - t-SNE Map", # Retained your manual title
    width=700, 
    height=1000
).configure_title(
    fontSize=18, anchor="start"
).configure_axis(
    labelFontSize=12, titleFontSize=14, grid=True # Retained your axis config
).configure_view(
    strokeWidth=0 # Retained your view config
)

# ===================================================================
# 4. GENERATE AND INJECT HTML (MANUAL FILTER HANDLING)
# ===================================================================

chart_json = final_chart.to_json()
topic_options_json = json.dumps(MY_TOPIC_OPTIONS)

# Load the HTML template from the Canvas (template.html)
try:
    with open("template.html", 'r') as f:
        html_template = f.read()
except FileNotFoundError:
    print("Error: template.html not found. Please ensure the file exists.")
    exit()

PLACEHOLDER = "<!-- Chart embedding script will be added here -->"

# Injection script handles chart embedding and manual dropdown wiring
injection_script = f"""
    <script>
      var spec = {chart_json};
      var topicOptions = {topic_options_json};
      
      var chartView;
      var selectElement = document.getElementById('topic-select');
      
      // 1. Populate the dropdown
      topicOptions.forEach(function(topic) {{
          var option = document.createElement('option');
          option.value = topic;
          option.text = topic;
          selectElement.appendChild(option);
      }});

      // 2. Initialize the chart (no controls_div option used)
      vegaEmbed('#vis', spec, {{ 
        actions: false, 
        mode: 'vega-lite',
      }}).then(result => {{
          chartView = result.view;
          
          // 3. Set up the change listener to update the 'topic_selection' signal
          selectElement.addEventListener('change', function() {{
              var selectedTopic = this.value;
              
              // Update the Altair parameter (signal) defined in the chart spec
              chartView.signal('topic_selection', selectedTopic).runAsync();
          }});
      }}).catch(console.error);
    </script>
"""

if PLACEHOLDER not in html_template:
     print("Error: Placeholder not found in template.html. Chart will not render.")
     final_html = html_template + injection_script
else:
    final_html = html_template.replace(PLACEHOLDER, injection_script)

with open("index.html", 'w') as f:
    f.write(final_html)