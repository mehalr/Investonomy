from django.urls import path
from finance.views import (
    fund_render,
    algo_trading_render,
    stock_render,
    dashboard_render,
    create_stock_model,
    get_week_forecast,
    get_sentiment,
)

app_name = 'finance'

urlpatterns = [
    path('algotrading/', algo_trading_render, name='algotrading'),
    path('dashboard/', dashboard_render, name='dashboard'),
    path('fund/', fund_render, name='fund'),
    path('get-stock-data/', create_stock_model, name='stock-model'),
    path('stock/', stock_render, name='stock'),
    path('week-stock-forecast', get_week_forecast, name='week-forecast'),
    path('sentiment', get_sentiment, name='sentiment'),
]
