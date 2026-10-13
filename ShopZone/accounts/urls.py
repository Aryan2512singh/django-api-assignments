from django.urls import path
from .views import (signup,send_otp,verify_otp,login_view,profile,logout_view,)

urlpatterns = [
    path("signup/", signup, name="signup"),
    path("send-otp/", send_otp, name="send-otp"),
    path("verify-otp/", verify_otp, name="verify-otp"),
    path("login/", login_view, name="login"),
    path("profile/", profile, name="profile"),
    path("logout/", logout_view, name="logout"),
]