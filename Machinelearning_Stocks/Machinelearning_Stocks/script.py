#!/usr/bin/env python

from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import precision_score
from datetime import datetime

import yfinance as yf
import pandas as pd

g= []
Tick=["AKER.OL","SALM.OL","MOWI.OL","TEL.OL","LSG.OL","ORK.OL","VEI.OL","NHY.OL","ATEA.OL"]

for i in range(len(Tick)):
    x = yf.Ticker(Tick[i])
    x = x.history(period="max")
    x.index = pd.to_datetime(x.index)
    x.index = x.index.strftime('%Y-%m-%d')
    del x["Dividends"]
    del x["Stock Splits"]
    x["Tomorrow"] = x["Close"].shift(-1)
    x["Target"] = (x["Tomorrow"] > x["Close"]).astype(int)

    # Create Additional Predictors
    horizons = [2, 5, 60, 250, 1000]
    new_predictors = []

    for horizon in horizons:
        rolling_averages = x.rolling(horizon).mean()

        ratio_column = f"Close_Ratio_{horizon}"
        x[ratio_column] = x["Close"] / rolling_averages["Close"]

        trend_column = f"Trend_{horizon}"
        x[trend_column] = x.shift(1).rolling(horizon).sum()["Target"]

        new_predictors += [ratio_column, trend_column]

    x = x.dropna(subset=x.columns[x.columns != "Tomorrow"])

    # Improved Model
    model = RandomForestClassifier(n_estimators=250, min_samples_split=50, random_state=1)

    def predict(train, test, predictors, model):
        model.fit(train[predictors], train["Target"])
        preds = model.predict_proba(test[predictors])[:, 1]
        preds[preds >= 0.58] = 1
        preds[preds < 0.58] = 0
        preds = pd.Series(preds, index=test.index, name="Predictions")
        combined = pd.concat([test["Target"], preds], axis=1)
        return combined

    # Backtesting with Improved Model
    def backtest(data, model, predictors, start=2500, step=250):
        all_predictions = []

        for i in range(start, data.shape[0], step):
            train = data.iloc[0:i].copy()
            test = data.iloc[i:(i + step)].copy()
            predictions = predict(train, test, predictors, model)
            all_predictions.append(predictions)

        return pd.concat(all_predictions)

    # Evaluate the Improved Model with Backtesting
    predictions = backtest(x, model, new_predictors)
    one = predictions['Predictions'].iloc[-1]
    two = precision_score(predictions["Target"], predictions["Predictions"])
    
    today_date = datetime.now().strftime('%Y-%m-%d')
    g.append([today_date, round(one), "{:.1%}".format(two), Tick[i]])
    

    # print("Prediction- " ,one , " Precision- " , "{:.1%}".format(two) , " Ticker: ", Tick[i] )
    
df = pd.DataFrame(g, columns=['Date', 'Predictions', 'Precision', 'Ticker']).style.hide()
folder_path = r'C:\Users\PC\Desktop\Stocks\Dates'
file_name = f'{datetime.today().strftime("%Y-%m-%d")}.xlsx'
file_path = f'{folder_path}\\{file_name}'

# Save DataFrame to Excel without headers
df.to_excel(file_path, index=False, header=False)