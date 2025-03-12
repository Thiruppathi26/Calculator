import dash 
from dash import dcc 
from dash import html 
from dash.dependencies import Output, Input, State 
from dash.exceptions import PreventUpdate 
from datetime import datetime as dt 
import yfinance as yf 
import pandas as pd 
import plotly.graph_objs as go 
import plotly.express as px 
 

from model import prediction 
 
app = dash.Dash(__name__, external_stylesheets=['assets/styles.css']) 
server = app.server 
 

item1 = html.Div([ 
        html.P("Welcome to the Stock Dash App!", className="start"), 
        html.Div([ 
            dcc.Input(id='stock-code', type='text', placeholder='Enter stock code'), 
            html.Button('Submit', id='submit-button') ], className="stock-input"), 
 
        html.Div([ 
            dcc.DatePickerRange( 
                id='date-range',  
                start_date=dt(2020, 1, 1).date(),  
                end_date=dt.now().date(),  
                className='date-input' 
            ) 
        ]), 
        html.Div([ 
            html.Button('Get Stock Price', id='stock-price-button'), 
            html.Button('Get Indicators', id='indicators-button'), 
            dcc.Input(id='forecast-days', type='number', placeholder='Enter number of days'), 
            html.Button('Get Forecast', id='forecast-button') 
        ], className="selectors") 
    ], 
 
 
 
 
    className="nav" 
) 
 
item2 = html.Div( 
    [ 
        html.Div( 
            [ 
                html.Img(id='logo', className='logo'), 
                html.H1(id='company-name', className='company-name') 
            ], 
            className="header"), 
        html.Div([], id="description"), 
        html.Div([], id="graphs-content"), 
        html.Div([], id="main-content"), 
        html.Div([], id="forecast-content") 
    ], 
    className="content" 
) 
 
app.layout = html.Div(className='container', children=[item1, item2]) 
 

 
@app.callback( 
    [ 
        Output("description", "children"), 
        Output("logo", "src"), 
        Output("company-name", "children"), 
        Output("stock-price-button", "n_clicks"), 
        Output("indicators-button", "n_clicks"), 
        Output("forecast-button", "n_clicks") 
    ], 
    [Input("submit-button", "n_clicks")], 
    [State("stock-code", "value")] 
) 
def update_data(n, val): 
    if n is None or val is None: 
        raise PreventUpdate 
    ticker = yf.Ticker(val) 
    inf = ticker.info 
    name = inf.get('longName', 'N/A') 
    logo_url = inf.get('logo_url', '') 
    description = inf.get('longBusinessSummary', 'No description available.') 
    return description, logo_url, name, None, None, None 
 
@app.callback( 
    
    [Output("graphs-content", "children")], 
    [ 
        Input("stock-price-button", "n_clicks"), 
        Input('date-range', 'start_date'), 
        Input('date-range', 'end_date')
    ], 
    [State("stock-code", "value")] 
) 
def stock_price(n, start_date, end_date, val): 
    if n is None or val is None: 
        raise PreventUpdate 
    try: 
        df = yf.download(val, start=start_date, end=end_date) 
    except Exception as e: 
        return [html.Div(f"Error fetching data: {e}")] 
 
    df.reset_index(inplace=True) 
    fig = px.line(
        df, x="Date", y=["Close", "Open"], title="Closing and Opening Price vs Date") 
    return [dcc.Graph(figure=fig)] 
 
@app.callback( 
    [Output("main-content", "children")], 
    [ 
        Input("indicators-button", "n_clicks"), 
        Input('date-range', 'start_date'), 
        Input('date-range', 'end_date') 
    ], 
    [State("stock-code", "value")] 
) 
def indicators(n, start_date, end_date, val): 
    if n is None or val is None: 
        raise PreventUpdate 
    try: 
        df_more = yf.download(val, start=start_date, end=end_date) 
    except Exception as e: 
        return [html.Div(f"Error fetching data: {e}")] 
 
    df_more.reset_index(inplace=True) 
    fig = get_more(df_more) 
    return [dcc.Graph(figure=fig)] 
 
def get_more(df): 
    if 'Close' in df: 
        df['EWA_20'] = df['Close'].ewm(span=20, adjust=False).mean() 
        fig = px.scatter(df, x="Date", y="EWA_20", title="Exponential Moving Average vs Date") 
        fig.update_traces(mode='lines+markers') 
        return fig 
    else: 
        return px.scatter(title="No closing data available for moving average calculation") 
 
@app.callback( 
    [Output("forecast-content", "children")], 

 
 
 
    [Input("forecast-button", "n_clicks")], 
    [State("forecast-days", "value"), 
     State("stock-code", "value")] 
) 
def forecast(n, n_days, val): 
    if n is None or val is None or n_days is None: 
        raise PreventUpdate 
    fig = prediction(val, int(n_days) + 1) 
    return [dcc.Graph(figure=fig)] 
 
if __name__ == '__main__': 
    app.run_server(debug=True)