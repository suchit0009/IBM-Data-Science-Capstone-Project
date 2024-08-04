# Import required libraries
import pandas as pd
import dash
from dash import dcc, html
from dash.dependencies import Input, Output
import plotly.express as px

# Read the SpaceX data into pandas dataframe
spacex_df = pd.read_csv("spacex_launch_dash.csv")

# Strip any leading/trailing whitespace from column names and values
spacex_df.columns = spacex_df.columns.str.strip()
spacex_df['Launch Site'] = spacex_df['Launch Site'].str.strip()

# Find min and max payload values for the range slider
min_payload = spacex_df['Payload Mass (kg)'].min()
max_payload = spacex_df['Payload Mass (kg)'].max()

# Create a dash application
app = dash.Dash(__name__)

# Create an app layout
app.layout = html.Div(children=[
    html.H1('SpaceX Launch Records Dashboard',
            style={'textAlign': 'center', 'color': '#503D36', 'font-size': 40}),

    # TASK 1: Add a dropdown list to enable Launch Site selection
    # The default select value is for ALL sites
    dcc.Dropdown(
        id='site-dropdown',
        options=[
            {'label': 'All Sites', 'value': 'ALL'},
            {'label': 'CCAFS LC-40', 'value': 'CCAFS LC-40'},
            {'label': 'KSC LC-39A', 'value': 'KSC LC-39A'},
            {'label': 'VAFB SLC-4E', 'value': 'VAFB SLC-4E'}
        ],
        value='ALL',
        placeholder="Select a Launch Site",
        searchable=True
    ),
    html.Br(),

    # TASK 2: Add a pie chart to show the total successful launches count for all sites
    # If a specific launch site was selected, show the Success vs. Failed counts for the site
    html.Div(dcc.Graph(id='success-pie-chart')),
    html.Br(),

    html.P("Payload range (Kg):"),
    
    # TASK 3: Add a slider to select payload range
    dcc.RangeSlider(
        id='payload-slider',
        min=0,
        max=10000,
        step=1000,
        marks={i: str(i) for i in range(0, 10001, 1000)},
        value=[min_payload, max_payload]
    ),

    # TASK 4: Add a scatter chart to show the correlation between payload and launch success
    html.Div(dcc.Graph(id='success-payload-scatter-chart')),
])

# TASK 2: Add a callback function for `site-dropdown` as input, `success-pie-chart` as output
@app.callback(
    Output('success-pie-chart', 'figure'),
    Input('site-dropdown', 'value')
)
def update_pie_chart(selected_site):
    if selected_site == 'ALL':
        # Aggregate success and failure counts for all sites
        total_counts = spacex_df['class'].value_counts()
        fig = px.pie(
            names=total_counts.index,
            values=total_counts.values,
            title='Total Launch Success Count'
        )
    else:
        # Filter data for the selected site
        site_data = spacex_df[spacex_df['Launch Site'] == selected_site]
        site_counts = site_data['class'].value_counts()
        fig = px.pie(
            names=site_counts.index,
            values=site_counts.values,
            title=f'Launch Success Count for {selected_site}'
        )
    return fig

# TASK 4: Add a callback function for `site-dropdown` and `payload-slider` as inputs, `success-payload-scatter-chart` as output
@app.callback(
    Output('success-payload-scatter-chart', 'figure'),
    [Input('site-dropdown', 'value'),
     Input('payload-slider', 'value')]
)
def update_scatter_plot(selected_site, payload_range):
    min_payload, max_payload = payload_range
    filtered_df = spacex_df[
        (spacex_df['Payload Mass (kg)'] >= min_payload) &
        (spacex_df['Payload Mass (kg)'] <= max_payload)
    ]

    if selected_site != 'ALL':
        filtered_df = filtered_df[filtered_df['Launch Site'] == selected_site]

    fig = px.scatter(
        filtered_df,
        x='Payload Mass (kg)',
        y='class',
        color='Booster Version Category',
        title=f'Payload vs. Success for {selected_site}' if selected_site != 'ALL' else 'Payload vs. Success for All Sites'
    )
    return fig

# Run the app
if __name__ == '__main__':
    app.run_server(port=8055, debug=True)
