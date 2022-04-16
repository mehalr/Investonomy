import pickle
import datetime
import pandas as pd
import threading

from django.shortcuts import render, redirect
from django.http import HttpResponse
from finance.utils import (
    get_stock_data,
    create_dataframe,
    LSTM_ALGO
)
from finance.models import (
    StockPredictionModel,
)
from finance.forex_algo_trading import algo_execute
from finance.market_sentiment_analysis import msa
from investonomy.settings import BASE_DIR
import json
import keras

model_path = BASE_DIR/'utilities\\'
mutual_fund_csv_path = BASE_DIR/'finance\\mutual_fund\\HMF.xlsx'


def algo_trading_render(request):
    if request.user.is_authenticated:
        context = {}
        context['active'] = 'algotrading'
        context['pairs'] = ['EUR/USD', 'GBP/USD', 'USD/CHF', 'AUD/USD', 'USD/CAD', 'EUR/JPY', 'USD/JPY', 'AUD/JPY', 'AUD/NZD', 'NZD/USD']
        if request.POST:
            pairs = request.POST.getlist('currencies')
            hours = request.POST['hours']
            token = request.POST['key']
            algo_script = threading.Thread(target=algo_execute, args=[pairs, hours, token])
            algo_script.start()
            # try:
            #     algo_trade = AlgoTradingModel.objects.get(user=request.user)
            #     algo_trade.api_key = token
            #     algo_trade.hours = hours
            #     algo_trade.started = True
            #     algo_trade.save()
            # except AlgoTradingModel.DoesNotExist:
            #     AlgoTradingModel.objects.create(user=request.user, api_key=token, hours=hours, started=True).save()
            context['running'] = 'true'
        return render(request, 'algotrading.html', context)
    return redirect('users:user-login')


def dashboard_render(request):
    if request.user.is_authenticated:
        context = {}
        context['active'] = 'dashboard'
        return render(request, 'dashboard.html', context)
    return redirect('users:user-login')


def fund_render(request):
    if request.user.is_authenticated:
        context = {}
        context['active'] = 'fund'
        df = pd.read_excel(mutual_fund_csv_path)
        context['schemes'] = df['Fund_Scheme_Name'].to_list()
        top_schemes = df[df['Good'] == 1][:5]
        companies = top_schemes['Fund_Scheme_Name'].to_list()
        context['companies'] = list(map(lambda x: x.split()[0], companies))

        context['sharpe'] = top_schemes['Sharpe_Ratio'].to_list()
        context['alpha'] = top_schemes['Alpha'].to_list()
        context['beta'] = top_schemes['Beta'].to_list()
        context['std_dev'] = top_schemes['Std_Dev'].to_list()
        context['one_year'] = top_schemes['1_Yr_Return'].to_list()
        context['three_year'] = top_schemes['3_Yr_Return'].to_list()
        context['five_year'] = top_schemes['5_Yr_Return'].to_list()

        if request.method == 'POST':
            fund_name = request.POST['scheme']
            fund = df[df['Fund_Scheme_Name'] == fund_name]
            context['risk'] = fund['Risk'].iloc[0]
            context['sr'] = fund['Sharpe_Ratio'].iloc[0]
            context['cat'] = fund['Category'].iloc[0]
            context['net'] = fund['Net_Return'].iloc[0]
            context['good'] = int(fund['Good'].iloc[0])
        return render(request, 'fund.html', context)
    return redirect('users:user-login')


def stock_render(request):
    if request.user.is_authenticated:
        context = {}
        context['active'] = 'stock'
        return render(request, 'stock.html', context)
    return redirect('users:user-login')


def get_week_stock_data(ticker):
    print(ticker)
    stock_data = get_stock_data(ticker)
    new_stock_data = []
    i = 0
    while len(new_stock_data) != 7 and i <= 31:
        try:
            stock_date = datetime.date.today() - datetime.timedelta(days=i)
            stock_date = stock_date.strftime('%Y-%m-%d')
            new_stock_data.append([float(stock_data['Time Series (Daily)'][stock_date]['4. close'])])
            i += 1
        except KeyError:
            i += 1
    return new_stock_data


def create_stock_model(request, ticker='IBM'):
    if request.POST:
        ticker = request.POST['ticker']
    try:
        stock = StockPredictionModel.objects.get(ticker=ticker)
        week_stock_data = get_week_stock_data(ticker)
        stock_model = keras.models.load_model(stock.predictor_path)
        stock_scaler = pickle.load(open(stock.scaler_path, 'rb'))
        week_stock_data = [[[i[0]] for i in stock_scaler.fit_transform(week_stock_data)]]
        prediction = stock_model.predict(week_stock_data)
        prediction = stock_scaler.inverse_transform(prediction)[0][0]
    except StockPredictionModel.DoesNotExist:
        stock_data = get_stock_data(ticker, 'full')
        stock_df = create_dataframe(stock_data)
        prediction = LSTM_ALGO(stock_df, ticker)
        path_model = f'{model_path}\\{ticker}'
        stock = StockPredictionModel.objects.create(ticker=ticker, predictor_path=path_model,
                                                    scaler_path=f'{path_model}\\scaler.pkl')
        stock.save()
    return HttpResponse(json.dumps({'name': 'hello', 'result': 'success', 'value': str(prediction)}), content_type='application/json')


def get_week_forecast(request, ticker='IBM'):
    if request.POST:
        if request.POST['ticker']:
            ticker = request.POST['ticker']
        stock = StockPredictionModel.objects.get(ticker=ticker)
        week_stock_data = get_week_stock_data(ticker)
        stock_model = keras.models.load_model(stock.predictor_path)
        stock_scaler = pickle.load(open(stock.scaler_path, 'rb'))
        week_stock_data = [[[i[0]] for i in stock_scaler.transform(week_stock_data)]]
        for i in range(7):
            prediction = stock_model.predict(week_stock_data)
            week_stock_data[0].pop(0)
            week_stock_data[0].append([prediction[0][0]])
        week_stock_data = stock_scaler.inverse_transform(week_stock_data[0])
        payload = {'result': 'success'}
        for i in range(7):
            payload[f'{i}'] = str(week_stock_data[i][0])
        return HttpResponse(json.dumps(payload), content_type='application/json')
    else:
        return HttpResponse(json.dumps({'result': 'error'}), content_type='application/json')


def get_sentiment(request):
    if request.POST:
        ticker = request.POST['ticker']
        close = request.POST['close']
        mean = request.POST['mean']
        payload = {}
        sentiment = msa(ticker, close, mean)
        payload['result'] = 'success'
        payload['idea'] = sentiment[0]
        payload['decision'] = sentiment[1]
        payload['positive'] = sentiment[2]
        payload['negative'] = sentiment[3]
        payload['neutral'] = sentiment[4]
        payload['polarity'] = sentiment[5]
        return HttpResponse(json.dumps(payload), content_type='application/json')
    else:
        return HttpResponse(json.dumps({'result': 'error'}), content_type='application/json')
