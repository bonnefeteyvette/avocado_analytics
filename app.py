import pandas as pd
from dash import Dash, Input, Output, dcc, html

# Load and prepare data
data = (
    pd.read_csv("avocado.csv")
    .assign(Date=lambda data: pd.to_datetime(data["Date"], format="%Y-%m-%d"))
    .sort_values(by="Date")
)
regions = data["region"].sort_values().unique()
avocado_types = data["type"].sort_values().unique()

# External stylesheet for font
external_stylesheets = [
    {
        "href": (
            "https://fonts.googleapis.com/css2?"
            "family=Lato:wght@400;700&display=swap"
        ),
        "rel": "stylesheet",
    },
]

# Initialize app
app = Dash(__name__, external_stylesheets=external_stylesheets)
app.title = "Avocado Analytics: Understand Your Avocados!"

# App layout
app.layout = html.Div(
    children=[
        html.Div(
            children=[
                html.P(children="🥑", className="header-emoji"),
                html.H1(children="Avocado Analytics", className="header-title"),
                html.P(
                    children=(
                        "Analyze the behavior of avocado prices and the number "
                        "of avocados sold in the US between 2015 and 2018"
                    ),
                    className="header-description",
                ),
            ],
            className="header",
        ),
        html.Div(
            children=[
                html.Div(
                    children=[
                        html.Div(children="Region", className="menu-title"),
                        dcc.Dropdown(
                            id="region-filter",
                            options=[{"label": region, "value": region} for region in regions],
                            value="Albany",
                            clearable=False,
                            className="dropdown",
                        ),
                    ]
                ),
                html.Div(
                    children=[
                        html.Div(children="Type", className="menu-title"),
                        dcc.Dropdown(
                            id="type-filter",
                            options=[
                                {"label": avocado_type.title(), "value": avocado_type}
                                for avocado_type in avocado_types
                            ],
                            value="organic",
                            clearable=False,
                            searchable=False,
                            className="dropdown",
                        ),
                    ]
                ),
                html.Div(
                    children=[
                        html.Div(children="Date Range", className="menu-title"),
                        dcc.DatePickerRange(
                            id="date-range",
                            min_date_allowed=data["Date"].min().date(),
                            max_date_allowed=data["Date"].max().date(),
                            start_date=data["Date"].min().date(),
                            end_date=data["Date"].max().date(),
                        ),
                    ]
                ),
            ],
            className="menu",
        ),
        html.Div(
            children=[
                html.Div(
                    children=dcc.Graph(
                        id="price-chart",
                        config={"displayModeBar": False},
                    ),
                    className="card",
                ),
                html.Div(
                    children=dcc.Graph(
                        id="volume-chart",
                        config={"displayModeBar": False},
                    ),
                    className="card",
                ),
                html.Div(
                    children=dcc.Graph(
                        id="top-region-chart",
                        config={"displayModeBar": False},
                    ),
                    className="card",
                ),
            ],
            className="wrapper",
        ),
    ]
)

# Callback
@app.callback(
    Output("price-chart", "figure"),
    Output("volume-chart", "figure"),
    Output("top-region-chart", "figure"),
    Input("region-filter", "value"),
    Input("type-filter", "value"),
    Input("date-range", "start_date"),
    Input("date-range", "end_date"),
)
def update_charts(region, avocado_type, start_date, end_date):
    filtered_data = data.query(
        "region == @region and type == @avocado_type and Date >= @start_date and Date <= @end_date"
    )
    # Convert to year
    filtered_data["Year"] = filtered_data["Date"].dt.year

    # Group by year for line charts
    yearly_data = (
        filtered_data.groupby("Year", as_index=False)
        .agg({"AveragePrice": "mean", "Total Volume": "sum"})
    )
    # Price chart
    price_chart_figure = {
    "data": [
        {
            "x": yearly_data["Year"],
            "y": yearly_data["AveragePrice"],
            "type": "scatter",  # Use scatter for full line+marker+text control
            "mode": "lines+markers+text",  # <-- This enables text to be shown
            "text": yearly_data["AveragePrice"].round(2),
            "textposition": "top center",
            "hovertemplate": "$%{y:.2f}<extra></extra>",
        }
    ],
    "layout": {
        "title": {"text": "Average Price of Avocados (Yearly)", "x": 0.05, "xanchor": "left"},
        "xaxis": {"title": "Year", "tickmode": "linear", "dtick": 1, "fixedrange": True},
        "yaxis": {"title": "Average Price", "tickprefix": "$", "fixedrange": True},
        "colorway": ["#17B897"],
     },
    }




    # Volume chart
    volume_chart_figure = {
    "data": [
        {
            "x": yearly_data["Year"],
            "y": yearly_data["Total Volume"],
            "type": "scatter",
            "mode": "lines+markers+text",
            "text": yearly_data["Total Volume"].round(0),
            "textposition": "top center",
            "hovertemplate": "%{y:,}<extra></extra>",
        }
    ],
    "layout": {
        "title": {"text": "Avocados Sold (Yearly)", "x": 0.05, "xanchor": "left"},
        "xaxis": {"title": "Year", "tickmode": "linear", "dtick": 1, "fixedrange": True},
        "yaxis": {"title": "Total Volume", "fixedrange": True},
        "colorway": ["darkgreen"],
     },
   }


     # Top 10 regions chart
    top_regions = (
        data.query("type == @avocado_type and Date >= @start_date and Date <= @end_date")
        .groupby("region", as_index=False)["Total Volume"]
        .sum()
        .sort_values("Total Volume", ascending=False)
        .head(10)
    )

    top_region_chart_figure = {
        "data": [
            {
            "type": "bar",
            "x": top_regions["Total Volume"], 
            "y": top_regions["region"],        
            "orientation": "h",                
            "text": top_regions["Total Volume"].round(0),
            "textposition": "auto",
            "marker": {"color": "darkcyan"},
            }
        ],
         "layout": {
        "title": {
            "text": "Top 10 Regions by Avocados Sold",
            "x": 0.05,
            "xanchor": "left"
        },
        "xaxis": {
            "title": "Total Volume",
            "tickformat": ",",  # Add comma for thousands
        },
        "yaxis": {
            "title": "Region",
            "autorange": "reversed",  # Top region at the top
        },
        "height": 500,  # Adjust height if needed
        "margin": {"l": 100, "r": 20, "t": 50, "b": 50},  # Ensure room for y-axis labels
    },
}

    return price_chart_figure, volume_chart_figure, top_region_chart_figure

    return price_chart_figure, volume_chart_figure, top_region_chart_figure

# Run the app
if __name__ == "__main__":
    app.run_server(debug=True)
