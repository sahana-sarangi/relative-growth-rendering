import altair as alt

PUBLIC_DATA_URL = "https://media.githubusercontent.com/media/sahana-sarangi/relative-growth-rendering/refs/heads/main/final_combined_data.csv"

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


topic_selection = alt.selection_point(
    fields=['TopicName'], 
    bind=alt.binding_select(
        name=' ', 
        # placeholder list
        options=['All Topics', 'Topic A', 'Topic B', 'Topic C'] 
    ), 
    empty='all' 
)


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

# Generate the Vega-Lite JSON specification
chart_json = final_chart.to_json()

# Read the custom HTML template file
with open("template.html", 'r') as f:
    html_template = f.read()

# Inject the chart JSON into the template's placeholder script block
final_html = html_template.replace(
    "",
    f"""
    <script>
      var spec = {chart_json};
      // The chart will be embedded in #vis, and controls in #filter-controls
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