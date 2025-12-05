import altair as alt
import json 
import pandas as pd 
import io 

# ===================================================================
# 1. CONFIGURATION & DATA SOURCE
# ===================================================================

# UPDATED: Reverting to the LFS media URL as the standard 'raw.githubusercontent.com' 
# path is confirmed to be consistently serving the LFS pointer file.
# This URL is more likely to serve the actual large file content to the browser, 
# even if it causes a hiccup in the Python topic loading step.
PUBLIC_DATA_URL = "https://media.githubusercontent.com/media/sahana-sarangi/relative-growth-rendering/main/final_combined_data.csv" 

# --- Data Loading and Topic Extraction (ONLY for the Dropdown) ---
# This block attempts to load the topics for the dropdown list.
try:
    # 1. Load data directly into Python using pandas.
    data_response = pd.read_csv(PUBLIC_DATA_URL) 
    
    # Check for empty columns and TopicName existence
    if data_response.empty:
        raise Exception("DataFrame loaded is empty. Check URL accessibility or file content.")
    
    if 'TopicName' not in data_response.columns:
        # This confirms the LFS pointer file issue (when it has only one column: 'version...')
        if len(data_response.columns) == 1 and data_response.columns[0].startswith('version'):
            print("CRITICAL LFS ERROR: The data URL is serving the Git LFS pointer file, not the CSV content.")
            print("Please ensure your 'final_combined_data.csv' file has been correctly pushed to Git LFS.")

        print(f"Error: 'TopicName' column not found. Available columns: {data_response.columns.tolist()}")
        raise KeyError("'TopicName' not found after loading.")
    
    # 2. Extract topics from the successfully loaded data
    unique_topics = data_response['TopicName'].unique().tolist()
    MY_TOPIC_OPTIONS = ['All Topics'] + sorted(unique_topics)
    
    # We are NOT embedding the data to keep the file size below 100MB.
    print("SUCCESS: Topic list loaded correctly from CSV.")

except Exception as e:
    # Fallback in case of data loading error
    print(f"Error loading data via pandas for topic list: {e}")
    MY_TOPIC_OPTIONS = ['All Topics', 'Topic List Error'] 
    
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

# UPDATED: Blue (Low/Negative) -> Tan (Neutral) -> Orange (High/Positive)
color_scale = alt.Scale(
    domain=[-0.2, purple_min, purple_max, max_growth],
    # Range is Blue (low), Tan (neutral low), Tan (neutral high), Orange (high)
    range=["#2c7bb6", "#f7f7d9", "#f7f7d9", "#fc8d59"]
)

# ===================================================================
# 3. CHART DEFINITION AND SELECTION LOGIC
# ===================================================================

# Define a simple parameter (signal) for the filter. This will be controlled manually by JavaScript.
topic_param = alt.param(name='topic_selection', value='All Topics')

# CRITICAL: Using URL reference for data to keep the file size below 100MB
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
    title="Year To Year Relative Growth - t-SNE Map", 
    width=700, 
    height=1000
).configure_title(
    fontSize=18, anchor="start"
).configure_axis(
    labelFontSize=12, titleFontSize=14, grid=True 
).configure_view(
    strokeWidth=0 
)

# ===================================================================
# 4. GENERATE AND INJECT HTML (MANUAL FILTER HANDLING)
# ===================================================================

# Convert the chart to JSON
# The resulting JSON will be small because it only contains the URL, not the 131MB of data.
chart_json = final_chart.to_json()

# Serialize the topic options for JavaScript
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
      // The Vega-Lite spec now references the data via URL, keeping the HTML file small
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
    print("SUCCESS: index.html generated with small file size.")