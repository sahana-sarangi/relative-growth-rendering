import altair as alt
import json 
import pandas as pd 
import io 

# ===================================================================
# 1. CONFIGURATION & DATA SOURCE
# ===================================================================

# FIX: Reverting to the original Dropbox URL. The GitHub link was serving a Git LFS pointer file.
# The Python script should be able to read this raw URL, and the data will be embedded into the chart.
PUBLIC_DATA_URL = "https://www.dropbox.com/scl/fi/gynl2pd6wpt5g9eift2s6/final_combined_data.csv?rlkey=v9rkbqc0bjc90fvcfso8m5ta4&st=mcfqrem2&dl=1" 

# --- Data Loading and Topic Extraction (CRITICAL FIX) ---
try:
    # 1. Load data directly into Python using pandas.
    # Reading from the Dropbox raw link
    data_response = pd.read_csv(PUBLIC_DATA_URL)
    
    # Check for empty columns (meaning data load failed)
    if data_response.empty or 'TopicName' not in data_response.columns:
        # Check if the data frame loaded anything at all
        if data_response.empty:
            raise Exception("DataFrame loaded is empty. Check URL accessibility or file content.")
        
        # If not empty but 'TopicName' is missing
        print(f"Error: 'TopicName' column not found. Available columns: {data_response.columns.tolist()}")
        raise KeyError("'TopicName' not found after loading.")
    
    # 2. Extract topics from the successfully loaded data
    unique_topics = data_response['TopicName'].unique().tolist()
    MY_TOPIC_OPTIONS = ['All Topics'] + sorted(unique_topics)
    
    # 3. Convert the DataFrame to JSON record format for direct injection into Altair
    # This bypasses web security restrictions that blocked the remote URL loading.
    DATA_VALUES_JSON = data_response.to_dict('records')

except Exception as e:
    # Fallback in case of data loading error
    print(f"Error loading data via pandas: {e}")
    MY_TOPIC_OPTIONS = ['All Topics', 'Data Load Failed'] 
    DATA_VALUES_JSON = [] 

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

# CRITICAL FIX: Use alt.Data(values=...) to inject the data directly
base = alt.Chart(alt.Data(values=DATA_VALUES_JSON)).properties(
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
chart_json = final_chart.to_json()

# Serialize the topic options for JavaScript
topic_options_json = json.dumps(MY_TOPIC_OPTIONS)

# Load the HTML template from the Canvas (template.html)
try:
    with open("template.html", 'r') as f:
        html_template = f.read()
except FileNotFoundError:
    # This error should be caught in the previous conversation step, but kept for robustness
    print("Error: template.html not found. Please ensure the file exists.")
    exit()

PLACEHOLDER = "<!-- Chart embedding script will be added here -->"

# Injection script handles chart embedding and manual dropdown wiring
injection_script = f"""
    <script>
      // The Vega-Lite spec already contains the data as embedded values (DATA_VALUES_JSON)
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