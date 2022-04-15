from django.urls import path
from users.views import (
    user_register,
    user_login,
    user_logout,
    user_reset_password
)


app_name = 'users'

urlpatterns = [
    path('password-reset/', user_reset_password, name='user-password-reset'),
    path('logout/', user_logout, name='logout'),
    path('signin/', user_login, name='user-login'),
    path('signup/', user_register, name='user-register'),
]
