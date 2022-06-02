
from dash import Dash, Input, Output,dcc, html
import time
from datetime import datetime
import pandas as pd
from plotly.subplots import make_subplots
import plotly.graph_objs as go
from neuralprophet import NeuralProphet
import numpy as np

interval = '1d' # 1d, 1wk, 1m
#ticker = '^GSPC' # 'AAPL,TSLA, AMZN,GOOGL,FDN,FB,^GSPC
#n_ma = 30
v = 'Adj Close' 
n = 180


period1 = int(time.mktime(datetime(2010,1,1,23,59).timetuple()))
period2 = int(time.mktime(datetime.now().timetuple()))

app = Dash(__name__)
server = app.server

app.layout = html.Div([
    dcc.Input(id="input-1", type="text", value="^GSPC"),
    dcc.Input(id='num-multi',type='number',value=60),
    dcc.Input(id="input-2", type="text", value="visualization"),
    #html.Button(id='submit-button-state', n_clicks=0, children='Submit'),
    dcc.Graph(id='graph-with-slider'),
            dcc.Slider(
            2010, #df['year'].min()
            2024, #df['year'].max()
            step=None,
            value=2010, #df['year'].min()
            marks={str(year): str(year) for year in range(2010,2022+3)}, #df['year'].unique()
            id='year-slider'
        )  
    
])


@app.callback(
    Output('graph-with-slider', 'figure'),
    Input('year-slider', 'value'),
    Input("input-1", 'value'),
    Input('num-multi', 'value'),
    Input("input-2", 'value')

    )
def update_figure(selected_year, ticker, n_ma,fcas):
    #query_string = f'https://query1.finance.yahoo.com/v7/finance/download/{ticker}?period1={period1}&period2={period2}&interval={interval}&events=history&includeAdjustedClose=true'
    x = "https://query1.finance.yahoo.com/v7/finance/download/"+str(ticker)+"?period1="+str(period1)+"&period2="+str(period2)+"&interval="+str(interval)+"&events=history"
    #print(x)
    df = pd.read_csv(x)

    if fcas == 'forecast':
        df['ds'] = df['Date']
        df['y'] = df['Adj Close']

        model = NeuralProphet(n_forecasts=360,n_lags=360,epochs=10)
        # fit your model
        if len(df)>=720:
            #fitted = model.fit(df[['ds','y']], freq='D')
            future = model.make_future_dataframe(df[['ds','y']][-720:], periods=360,n_historic_predictions=720)
        else: 
            future = model.make_future_dataframe(df[['ds','y']], periods=360,n_historic_predictions=len(df))
        
        forecast = model.predict(future)

        chart = forecast[['ds','y','yhat360']]
        chart['ds'] = chart['ds'].astype("datetime64")
        
        f = chart.iloc[np.isnan(chart['y'].values)]
        combo = pd.concat([df,f])
        combo['Date'] = combo['ds'].astype("datetime64")
        combo['Prediction'] = combo['yhat360']
        combo = combo.set_index("Date")
        combo["date"] = combo["ds"].astype("datetime64")
        combo["year"] = combo["ds"].astype("datetime64").dt.year
    else:
        combo = df.copy()
        combo["date"] = combo["Date"].astype("datetime64")
        combo["year"] = combo["Date"].astype("datetime64").dt.year

    filtered_df = combo[combo.year >= selected_year]
    filtered_df[str(n_ma) + 'day_rolling_avg'] = filtered_df[v].rolling(n_ma).mean()

    #fig = px.line(filtered_df, x="date", y=[v,str(n_ma) + 'day_rolling_avg'])
    #fig.update_layout() #transition_duration=500
    fig = make_subplots(rows=3, cols=2,subplot_titles=['Adj Close +High +Low +Moving Average', 'Volume', 'High', 'Low','Open', 'Close'])

    fig.add_trace(go.Scatter(x=filtered_df['date'], y=filtered_df['High'], mode="lines"),row=1, col=1) #, marker=dict(color='#17becf'))
    fig.add_trace(go.Scatter(x=filtered_df['date'], y=filtered_df['Low'], mode="lines"),row=1, col=1) #,marker=dict(color='#1f77b4'))
    fig.add_trace(go.Scatter(x=filtered_df['date'], y=filtered_df['Adj Close'], mode="lines"),row=1, col=1)  #, marker=dict(color='#bcbd22'))
    if fcas == "forecast":
        fig.add_trace(go.Scatter(x=filtered_df['date'], y=filtered_df['Prediction'], mode="lines"),row=1, col=1)  #, marker=dict(color='#bcbd22'))
    fig.add_trace(go.Scatter(x=filtered_df['date'], y=filtered_df[str(n_ma) + 'day_rolling_avg'], mode="lines"),row=1, col=1)  #, marker=dict(color='#bcbd22'))
    
    fig.add_trace(go.Bar(x=filtered_df['date'], y=filtered_df['Volume'],marker=dict(color="blue")), row=1, col=2)
    
    fig.add_trace(go.Scatter(x=filtered_df['date'], y=filtered_df['High'], mode="lines"), row=2,col=1)
    fig.add_trace(go.Scatter(x=filtered_df['date'], y=filtered_df[str(n_ma) + 'day_rolling_avg'], mode="lines"),row=2, col=1)  #, marker=dict(color='#bcbd22'))
    
    fig.add_trace(go.Scatter(x=filtered_df['date'], y=filtered_df['Low'], mode="lines"),row=2,col=2)
    fig.add_trace(go.Scatter(x=filtered_df['date'], y=filtered_df[str(n_ma) + 'day_rolling_avg'], mode="lines"),row=2, col=2)  #, marker=dict(color='#bcbd22'))
    

    fig.add_trace(go.Scatter(x=filtered_df['date'], y=filtered_df['Open'], mode="lines"),row=3,col=1)
    fig.add_trace(go.Scatter(x=filtered_df['date'], y=filtered_df[str(n_ma) + 'day_rolling_avg'], mode="lines"),row=3, col=1)  #, marker=dict(color='#bcbd22'))
    
    fig.add_trace(go.Scatter(x=filtered_df['date'], y=filtered_df['Close'], mode="lines"),row=3,col=2)
    fig.add_trace(go.Scatter(x=filtered_df['date'], y=filtered_df[str(n_ma) + 'day_rolling_avg'], mode="lines"),row=3, col=2)  #, marker=dict(color='#bcbd22'))
    
    fig.update_layout(height=1200, width=1300, title_text=ticker,showlegend=False)
    fig.update_xaxes(rangeslider_visible=True,gridwidth=5,rangeslider_thickness = 0.05)
    #fig.show()

    return fig



if __name__ == '__main__':
    app.run_server(debug=True, host='0.0.0.0', port=8080)
