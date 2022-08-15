import requests
import pandas as pd
import numpy as np
import math
import pickle
import matplotlib.pyplot as plt

from keras.models import Sequential
from keras.layers import Dense
from keras.layers import Dropout
from keras.layers import LSTM

from sklearn.metrics import mean_squared_error
from sklearn.preprocessing import MinMaxScaler

from investonomy.settings import BASE_DIR


model_path = BASE_DIR/'utilities'


def get_stock_data(symbol, size='compact'):
    api_key = '8Z7MAVSSG2H39LQN'
    url = f'https://www.alphavantage.co/query?function=TIME_SERIES_DAILY&outputsize={size}&symbol={symbol}&apikey={api_key}'
    r = requests.get(url)
    data = r.json()
    return data


def create_dataframe(data):
    df = pd.DataFrame(data["Time Series (Daily)"])
    df = df.T
    df.reset_index(inplace=True)
    df.columns = ['time', 'open', 'high', 'low', 'close', 'volume']
    df = df[:1000]
    df = df.iloc[::-1]
    return df


def LSTM_ALGO(df, sym):
    dataset_train = df.iloc[0:int(0.8 * len(df)), :]
    dataset_test = df.iloc[int(0.8 * len(df)):, :]
    training_set = df.iloc[:, 4:5].values

    sc = MinMaxScaler(feature_range=(0, 1))  # Scaled values btween 0,1
    print("Training Set")
    print(training_set)
    training_set_scaled = sc.fit_transform(training_set)

    X_train = []
    y_train = []
    for i in range(7, len(training_set_scaled)):
        X_train.append(training_set_scaled[i - 7:i, 0])
        y_train.append(training_set_scaled[i, 0])
    X_train = np.array(X_train)
    y_train = np.array(y_train)
    X_forecast = np.array(X_train[-1, 1:])
    X_forecast = np.append(X_forecast, y_train[-1])
    X_train = np.reshape(X_train, (X_train.shape[0], X_train.shape[1], 1))  # .shape 0=row,1=col
    X_forecast = np.reshape(X_forecast, (1, X_forecast.shape[0], 1))

    regressor = Sequential()

    regressor.add(LSTM(units=50, return_sequences=True, input_shape=(X_train.shape[1], 1)))
    regressor.add(Dropout(0.1))

    regressor.add(LSTM(units=50, return_sequences=True))
    regressor.add(Dropout(0.1))

    regressor.add(LSTM(units=50, return_sequences=True))
    regressor.add(Dropout(0.1))

    regressor.add(LSTM(units=50))
    regressor.add(Dropout(0.1))

    regressor.add(Dense(units=1))

    regressor.compile(optimizer='adam', loss='mean_squared_error')

    regressor.fit(X_train, y_train, epochs=25, batch_size=32)

    dataset_test['close'] = dataset_test['close'].apply(lambda x: float(x))
    real_stock_price = dataset_test.iloc[:, 4:5].values


    dataset_total = pd.concat((dataset_train['close'], dataset_test['close']), axis=0)
    testing_set = dataset_total[len(dataset_total) - len(dataset_test) - 7:].values
    testing_set = testing_set.reshape(-1, 1)

    testing_set = sc.transform(testing_set)

    X_test = []
    for i in range(7, len(testing_set)):
        X_test.append(testing_set[i - 7:i, 0])
        # Convert list to numpy arrays
    X_test = np.array(X_test)

    X_test = np.reshape(X_test, (X_test.shape[0], X_test.shape[1], 1))

    predicted_stock_price = regressor.predict(X_test)
    predicted_stock_price = sc.inverse_transform(predicted_stock_price)

    fig = plt.figure(figsize=(7.2, 4.8), dpi=65)
    plt.plot(real_stock_price, label='Actual Price')
    plt.plot(predicted_stock_price, label='Predicted Price')

    plt.legend(loc=4)
    plt.savefig('LSTM.png')
    plt.close(fig)

    regressor.save(f'{model_path}\\{sym}')
    pickle.dump(sc, open(f'{model_path}\\{sym}\\scaler.pkl', 'wb'))


    predicted_stock_price = sc.inverse_transform(predicted_stock_price)
    print('predicted_stock_p')

    error_lstm = math.sqrt(mean_squared_error(real_stock_price, predicted_stock_price))

    forecasted_stock_price = regressor.predict(X_forecast)
    print('Model Predict Test')
    print(X_forecast)

    forecasted_stock_price = sc.inverse_transform(forecasted_stock_price)
    print('Forecasted Stock Price')
    print(forecasted_stock_price)

    lstm_pred = forecasted_stock_price[0, 0]
    return lstm_pred
