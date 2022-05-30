import time
from datetime import datetime
import pandas as pd
from dash import Dash, dash_table
from main import update_figure

interval = '1d' # 1d, 1wk, 1m
ticker = '^GSPC' # 'AAPL,TSLA, AMZN,GOOGL,FDN,FB,^GSPC

period1 = int(time.mktime(datetime(2000,1,1,23,59).timetuple()))
period2 = int(time.mktime(datetime.now().timetuple()))

#df = pd.read_csv('https://query1.finance.yahoo.com/v7/finance/download/^GSPC?period1=946799940&period2=1653934759&interval=1d&events=history&includeAdjustedClose=true')
x = "https://query1.finance.yahoo.com/v7/finance/download/"+str(ticker)+"?period1="+str(period1)+"&period2="+str(period2)+"&interval="+str(interval)+"&events=history"
#print(x)
df = pd.read_csv(x)
print(df.head(3))

#app = Dash(__name__)

#app.layout = dash_table.DataTable(df.to_dict('records'), [{"name": i, "id": i} for i in df.columns])

#if __name__ == '__main__':
#    app.run_server(debug=True)



