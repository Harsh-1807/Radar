import pandas as pd
import plotly.express as px
import plotly.io as pio
import os

def generate_html(csv_file_path):
    # Check if the CSV file exists
    if not os.path.exists(csv_file_path):
        print(f"File {csv_file_path} does not exist.")
        return

    # Read the CSV file
    df = pd.read_csv(csv_file_path)

    # Create a Plotly scatter plot with circular markers
    scatter_fig = px.scatter(
        df,
        x='latitude',
        y='longitude',
        color='distance',
        size='speed',
        hover_name='timestamp',
        title='Scatter Plot of Radar Detection',
        labels={'latitude': 'Latitude', 'longitude': 'Longitude', 'distance': 'Distance', 'speed': 'Speed'},
        color_continuous_scale=px.colors.sequential.Viridis
    )
    
    # Update marker properties
    scatter_fig.update_traces(
        marker=dict(
            size=10,  # Adjust the size for better visibility
            symbol='circle'  # Use circle shape
        )
    )

    # Create a Plotly bar chart for speeds
    bar_fig = px.bar(
        df,
        x='timestamp',
        y='speed',
        title='Bar Chart of Speeds',
        labels={'timestamp': 'Timestamp', 'speed': 'Speed'},
        color='speed',
        color_continuous_scale=px.colors.sequential.Plasma
    )

    # Create a Plotly line chart for distance over time
    line_fig = px.line(
        df,
        x='timestamp',
        y='distance',
        title='Line Chart of Distance Over Time',
        labels={'timestamp': 'Timestamp', 'distance': 'Distance'},
        markers=True
    )

    # Convert plots to HTML
    scatter_html = pio.to_html(scatter_fig, full_html=False)
    bar_html = pio.to_html(bar_fig, full_html=False)
    line_html = pio.to_html(line_fig, full_html=False)

    # Generate HTML table
    table_html = df.to_html(classes='data', border=0)

    # HTML template with plots and table
    html_content = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <title>Radar Detection Log</title>
        <style>
            body {{
                font-family: Arial, sans-serif;
                display: flex;
                flex-direction: row;
                justify-content: space-between;
                padding: 20px;
            }}
            .container {{
                display: flex;
                flex-direction: row;
                justify-content: space-between;
                width: 100%;
            }}
            .plot-container {{
                width: 60%;
                display: flex;
                flex-direction: column;
                gap: 20px;
            }}
            .table-container {{
                width: 38%;
                border: 1px solid #ccc;
                padding: 10px;
                border-radius: 5px;
            }}
            table {{
                width: 100%;
                border-collapse: collapse;
            }}
            th, td {{
                padding: 8px;
                text-align: left;
                border-bottom: 1px solid #ddd;
            }}
            th {{
                background-color: #f4f4f4;
            }}
        </style>
    </head>
    <body>
        <div class="container">
            <div class="plot-container">
                <div class="plot">{scatter_html}</div>
                <div class="plot">{bar_html}</div>
                <div class="plot">{line_html}</div>
            </div>
            <div class="table-container">
                {table_html}
            </div>
        </div>
    </body>
    </html>
    """

    # Write the HTML content to a file with UTF-8 encoding
    html_file_path = 'detection_log_visualization.html'
    with open(html_file_path, 'w', encoding='utf-8') as f:
        f.write(html_content)

    # Open the HTML file in the default web browser
    os.system(f'start {html_file_path}' if os.name == 'nt' else f'xdg-open {html_file_path}')

if __name__ == "__main__":
    # Path to the CSV file
    csv_file_path = 'detection_log.csv'
    generate_html(csv_file_path)
