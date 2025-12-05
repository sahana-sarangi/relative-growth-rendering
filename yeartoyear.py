import altair as alt

PUBLIC_DATA_URL = "https://media.githubusercontent.com/media/sahana-sarangi/relative-growth-rendering/refs/heads/main/final_combined_data.csv"

min_tsne_x = -90.0  # Placeholder 
max_tsne_x = 90.0   # Placeholder
min_tsne_y = -90.0  # Placeholder
max_tsne_y = 90.0   # Placeholder
max_growth = 0.6    # Placeholder

purple_center = 0.05
purple_range = 0.02
purple_min = purple_center - purple_range / 2
purple_max = purple_center + purple_range / 2

color_scale = alt.Scale(
    domain=[-0.2, purple_min, purple_max, max_growth],
    range=["#4575b4", "#762a83", "#762a83", "#d73027"]
)

final_chart = (
    alt.Chart(
        alt.Data(
            url=PUBLIC_DATA_URL,
            format=alt.DataFormat(type='csv', parse={"Year": "integer", "TSNE-x": "number", "TSNE-y": "number", "RelativeGrowthRate": "number"})
        )
    )
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

final_chart.save("index.html")
