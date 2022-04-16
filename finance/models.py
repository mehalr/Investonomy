from django.db import models
from django.contrib.auth.models import User
from django.contrib.auth.signals import user_logged_in
from datetime import datetime


class StockPredictionModel(models.Model):
    ticker = models.CharField(unique=True, blank=False, max_length=32)
    scaler_path = models.CharField(unique=True, blank=True, max_length=512)
    predictor_path = models.CharField(unique=True, blank=True, max_length=512)
    current_prediction = models.CharField(blank=True, max_length=32)
    current_prediction_date = models.DateField(auto_now=True)

    def __str__(self):
        return self.ticker

    def get_model(self):
        return self.predictor_path

    def get_scaler(self):
        return self.scaler_path

    def get_current_prediction(self):
        return self.current_prediction

    def get_current_prediction_date(self):
        return self.current_prediction_date


class AlgoTradingModel(models.Model):
    api_key = models.CharField(max_length=64, unique=True)
    user = models.OneToOneField(User, related_name='user', on_delete=models.CASCADE)
    hours = models.IntegerField(blank=True)
    started = models.BooleanField(default=False)
    last_updated = models.DateField(auto_now=True)

    def __str__(self):
        return self.user

    def get_last_updated(self):
        return self.last_updated


#
# def check_algo_running(sender, user, request, **kwargs):
#     if datetime.now() -
