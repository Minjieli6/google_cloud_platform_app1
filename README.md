# Stock Visualizer Application on Google Cloud Platform<!-- omit in toc -->

[![CI](https://github.com/Minjieli6/google_cloud_platform_app1/actions/workflows/main.yml/badge.svg)](https://github.com/Minjieli6/google_cloud_platform_app1/actions/workflows/main.yml)

- [I. Project Overview](#i-project-overview)
    - [Architecture Diagram](#architecture-diagram)
- [II. Source code stored in GitHub](#ii-source-code-stored-in-github)
    - [Real Time Extraction](#real-time-extraction)
    - [Google Cloud Storage](#google-cloud-storage)
- [III. Continuous Deployment from CircleCI](#iii-continuous-deployment-from-circleci)
- [IV. ML predictions created and served out (AutoML, BigQuery, etc.)](#iv-ml-predictions-created-and-served-out-automl-bigquery-etc)
    - [NeuralProphet](#neuralprophet)
    - [GCP BigQuery ML](#gcp-bigquery-ml)
- [V. Stackdriver installed for monitoring](#v-stackdriver-installed-for-monitoring)
- [VI. Deployed into GCP environment with Cloud Run](#vi-deployed-into-gcp-environment-with-cloud-run)
    - [Deploy to GCP Cloud Run](#deploy-to-gcp-cloud-run)
    - [Deploy locally](#deploy-locally)
- [VII. Result and Demo](#vii-result-and-demo)
    - [Input Parameters](#input-parameter)
    - [App Link](#app-link)
    - [Demo Link](#demo-link)

## **I. Project Overview**
In this project, we build an application to visualize stock market data from Yahoo Finance and its forecasting of market movement over time through the architecture pipeline shown in Figure 1. 

### **App link:** https://googlecloudplatformapp1-hmlu6pvwmq-ue.a.run.app/
### **Demo link:** https://youtu.be/wIXzjELHWNQ

### **Architecture Diagram**
<br></br>
![](0_architecture_diagram.png)

Figure 1: Architecture diagram

## **II. Source Code Stored in GitHub**
Our source codes are stored in GitHub repo https://github.com/Minjieli6/google_cloud_platform_app1. It can be easily cloned with the following code. 

```python
git clone git@github.com:Minjieli6/google_cloud_platform_app1.git
cd google_cloud_platform_app1/
virtualenv ~/.venv && source ~/.venv/bin/activate
make all
#Your code has been rated at 10.00/10 (previous run: 10.00/10, +0.00)
```
Below is the list of files contained in this repo. 

***requirements.txt*** stores all the libraries, modules, and packages on which the Python project is dependent or requires to run, such as pytest, pylint, dash, plotly, jinjia2, gunicorn, etc. 

***Makefile*** defines set of tasks to be executed and simplifies automating software building procedures and complex tasks with dependencies. 

***main.py*** contains the main part of the application, including ***Dash*** server and layout. 

***test_main.py*** is a test file to check if the open source is available.  

***Dockerfile*** is used to execute all the commands to automatically build an image of the application. 

***app.yaml*** specifies how URL paths correspond to request handlers and runs the ***Dash*** app on GCP using ***gunicorn***. 
<br></br>

## **III. Continuous Deployment from CircleCI**
The file ***main.yml*** under the folder ***.github/workflows/*** has been set up for [**GitHub Actions**](https://github.com/Minjieli6/google_cloud_platform_app1/actions) workflow. The credentials have been set up by using SSH keys from GCP Security via secret manager with identity aware proxy. The code below is used to pull and push the code to GitHub from GCP terminal. 

``` js
git status
git add *
git commit -m "merging code"
git config --global user.email "minjieli6@gmail.com"
git config --global user.name "Minjieli6"
git pull
git push
```

## **IV. Data stored in GCP (BigQuery, Google Cloud Storage, etc.)**
### **Real Time Extraction**

We get the stock market data from [Yahoo Finance](https://finance.yahoo.com/quote/%5EGSPC?p=^GSPC&.tsrc=fin-srch) with several input parameters, such as stock symbol, starting time, ending time, and frequency through an URL as below. In this case, it’s unnecessary to store data into Google Cloud Storage since we’re able to leverage the real-time extraction.  

```js
interval = '1d'
ticker = '^GSPC'
period1 = int(time.mktime(datetime(2010,1,1,23,59).timetuple()))
period2 = int(time.mktime(datetime.now().timetuple()))

query_string = f"https://query1.finance.yahoo.com/v7/finance/download/{ticker}?period1={period1}&period2={period2}&interval={interval}&events=history&includeAdjustedClose=true"

df = pd.read_csv(query_string)
print(df.head(3))
```

![](5_stock_market_data_from_yahoo_finance.png)

### **Google Cloud Storage**

Alternatively, we can upload data to Google Cloud Storage, and then use Google Cloud Function to schedule data updates through Google Cloud Scheduler in Figure 6. 

![](6_GCP_Cloud_Storage.png)

Figure 2: Cloud Storage for BigQuery ML

## **IV.	ML predictions created and served out (AutoML, BigQuery, etc.)**

### **NeuralProphet**

The model **NeuralProphet** is embedded in the app to predict future values based on history data. [NeuralProphet](https://arxiv.org/abs/2111.15397), a python library for time series model based on neural network, is built on top of PyTorch and inspired by Facebook Prophet and AR-Net library. NeuralProphet optimizes gradient descent with PyTorch, applies AR-Net for autocorrelation, leverages a separate Feed-Forward Neural Network (FFNN) for lagged regressors, and configure non-linear deep layers of the FFNNs. 

```js
from neuralprophet import NeuralProphet

df['ds'] = df['Date']
df['y'] = df['Adj Close']

model = NeuralProphet(n_forecasts=360,n_lags=360,epochs=100)
model.fit(df[['ds','y']], freq='D')
future = model.make_future_dataframe(df[['ds','y']], periods=360,n_historic_predictions=len(df))
forecast = model.predict(future)

model.plot_components(forecast)
```
![](7_snp_decomposition.png)

Figure 4.1: S&P time series decomposition 

### **GCP BigQuery ML**

Alternatively, we can easily create an end-to-end AutoML model ARIMA for training and forecasting the stock with **BigQuery ML**. In Figure 4, we train and deploy ML models directly in SQL, then visualize the forecasted values with Data Studio in Figure 5. In BigQuery ML, data is auto preprocessed with missing value imputation, timestamp de-duplication, anomalies identification, holiday effects, seasonal and trend decomposition. The best model is generated with the lowest AIC score. Time-series model Auto ARIMA can be scheduled to retrain automatically. The result can be load and displayed in Python using the code below. 


![](8_ARIMA_BigQueryML.png)

Figure 4.2: Create an ARIMA model in SQL with BigQuery ML 

![](9_forecast_BigQueryML.png)

Figure 4.3: S&P time series decomposition 

```js
from google.cloud import bigquery

gcp_project = 'i-mariner-347323'
db_project = 'Dataset'

client = bigquery.Client(project=gcp_project)
dataset_ref = client.dataset(db_project)

def gcp2df(sql):
	query = client.query(sql)
	results = query.result()
	return results.to_dataframe()

qry = """SELECT * FROM `i-mariner-347323.Dataset.AMZN_output`"""

print(df.head())

fig = px.line(df, x="timestamp", y=df.columns, title='Amazon Stock Price')
fig.show()
```

## **V.	Stackdriver installed for monitoring**
Google Cloud’s operation suite, formerly called stackdriver, integrated monitoring, logging, and trace managed services for applications and systems running on Google Cloud. It not only provides visibility into the performance, uptime, and overall health of the app, but also enables users to set alerts and notify if metrics are in the expected ranges. Cloud logging in Figure 6 shows real-time logs and helps improve troubleshooting and debugging. Cloud monitoring in Figure 7 is a custom dashboard for us to track the usages of container’s memory and CPU, as well log entries etc. Cloud trace in Figure 8 collects latency data from the app and tracks how request propagate through the app.  

![](10_GCP_cloud_logging.png)

Figure 5.1: GCP cloud logging

![](11_GCP_cloud_monitoring.png)

Figure 5.2: Cloud monitoring custom dashboard 

![](12_GCP_Cloud_trace.png)

Figure 5.3: Cloud trace

## **VI. Deployed into GCP environment with Cloud Run**

### **Deploy to GCP Cloud Run**

The app is built with Dockerfile and deployed container to **Cloud Run** service [googlecloudplatformapp1] in project [second-strand-351703] region [us-east1] in Figure 6.1. 

![](15_GCP_deployment.png)

Figure 6.1: Deployed into GCP environment with Cloud Run

```js
make all
gcloud run deploy
```

This code is used to deploy the container to cloud run. We can see the API traffic, errors, and median latency in Figure 6.2. Once it deployed, there are more comprehensive metrics including request and instant count in Cloud Run metrices as Figure 6.3. 


![](10_GCP_cloud_logging.png)

Figure 6.2: GCP cloud logging

![](11_GCP_cloud_monitoring.png)

Figure 6.3: Cloud monitoring custom dashboard 

![](12_GCP_Cloud_trace.png)

Figure 6.4: Cloud trace

### **Deploy locally**
Alternatively, the app can be easily deployed with local host by using the code below. 
```js
make install
python main.py
```

## **VII.	Result and Demo**
The **interactive** results with **plotly dash** display high, low, adjusted closed, moving average, and next 360 days forecasted values in Figure 16. Demo is also attached. 

### **Input Parameters:**
* 1st text input: stock symbol (such as ^GSPC, ^DJI, or FDN etc)
* 2nd numeric input: number of days moving average (such as 30, 60, 90, 120 etc)
* 3nd text input: (such as visualization or forecast)
    * **visualization** only for historical data  
    * **forecast** for both historical and forecasted values
        * Note: the *forecast* part is not stable, it may require a time delay to allow model training, fitting and predicting
            ```js 
            time.sleep(30) 
            ```
* time sliders:
    * **year slicer** for all the charts at the bottom of the web
    * **range slicer** for individual chart

### **App link:** https://googlecloudplatformapp1-hmlu6pvwmq-ue.a.run.app/
### **Demo link:** https://youtu.be/wIXzjELHWNQ

**Click the chart below for Demo video**
[![Watch the video](16_app_result.png)](https://youtu.be/wIXzjELHWNQ)

Figure 7: Historical and forecasted values on the deployed app

