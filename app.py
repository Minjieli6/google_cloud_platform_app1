
from dash import Dash, Input, Output,dcc, html
#import plotly.express as px
import time
from datetime import datetime
import pandas as pd
from plotly.subplots import make_subplots
import plotly.graph_objs as go


interval = '1d' # 1d, 1wk, 1m
#ticker = '^GSPC' # 'AAPL,TSLA, AMZN,GOOGL,FDN,FB,^GSPC
#n_ma = 30
v = 'Adj Close' 
n = 180


period1 = int(time.mktime(datetime(2010,1,1,23,59).timetuple()))
period2 = int(time.mktime(datetime.now().timetuple()))

app = Dash(__name__)

app.layout = html.Div([
    dcc.Input(id="input-1", type="text", value="^GSPC"),
    dcc.Input(id='num-multi',type='number',value=15),
    #dcc.Input(id="input-2", type="number", value=2021),
    #html.Button(id='submit-button-state', n_clicks=0, children='Submit'),
    dcc.Graph(id='graph-with-slider'),
            dcc.Slider(
            2010, #df['year'].min()
            2022, #df['year'].max()
            step=None,
            value=2010, #df['year'].min()
            marks={str(year): str(year) for year in range(2010,2022+1)}, #df['year'].unique()
            id='year-slider'
        )  
    
])


@app.callback(
    Output('graph-with-slider', 'figure'),
    Input('year-slider', 'value'),
    #Input("input-2", 'value'),
    Input('num-multi', 'value'),
    Input("input-1", 'value'),

    )
def update_figure(selected_year, n_ma, ticker):
    #query_string = f'https://query1.finance.yahoo.com/v7/finance/download/{ticker}?period1={period1}&period2={period2}&interval={interval}&events=history&includeAdjustedClose=true'
    x = "https://query1.finance.yahoo.com/v7/finance/download/"+str(ticker)+"?period1="+str(period1)+"&period2="+str(period2)+"&interval="+str(interval)+"&events=history"
    #print(x)
    df = pd.read_csv(x)
    df["date"] = df["Date"].astype("datetime64")
    df["year"] = df["Date"].astype("datetime64").dt.year

    filtered_df = df[df.year >= selected_year]
    filtered_df[str(n_ma) + 'day_rolling_avg'] = df[v].rolling(n_ma).mean()

    #fig = px.line(filtered_df, x="date", y=[v,str(n_ma) + 'day_rolling_avg'])
    #fig.update_layout() #transition_duration=500
    fig = make_subplots(rows=3, cols=2,subplot_titles=['Adj Close +High +Low +Moving Average', 'Volume', 'High', 'Low','Open', 'Close'])

    fig.add_trace(go.Scatter(x=filtered_df['date'], y=filtered_df['High'], mode="lines"),row=1, col=1) #, marker=dict(color='#17becf'))
    fig.add_trace(go.Scatter(x=filtered_df['date'], y=filtered_df['Low'], mode="lines"),row=1, col=1) #,marker=dict(color='#1f77b4'))
    fig.add_trace(go.Scatter(x=filtered_df['date'], y=filtered_df['Adj Close'], mode="lines"),row=1, col=1)  #, marker=dict(color='#bcbd22'))
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
    app.run_server(debug=True)
