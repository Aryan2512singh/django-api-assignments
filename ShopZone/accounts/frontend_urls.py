from django.urls import path
from django.shortcuts import render


def login_page(request):
    return render(request, "accounts/login.html")


def signup_page(request):
    return render(request, "accounts/signup.html")


def verify_otp_page(request):
    return render(request, "accounts/verify_otp.html")


def profile_page(request):
    return render(request, "accounts/profile.html")


urlpatterns = [
    path("login/", login_page, name="login-page"),
    path("signup/", signup_page, name="signup-page"),
    path("verify-otp/", verify_otp_page, name="verify-otp-page"),
    path("profile/", profile_page, name="profile-page"),
]