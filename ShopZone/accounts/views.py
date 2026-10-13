
from datetime import timedelta
import secrets

from django.conf import settings
from django.contrib.auth import authenticate
from django.core.mail import send_mail
from django.utils import timezone

from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from rest_framework_simplejwt.exceptions import TokenError
from rest_framework_simplejwt.tokens import RefreshToken

from .models import EmailVerification, User
from .permissions import IsVerifiedUser
from .serializers import SignupSerializer, UserSerializer


OTP_LIFETIME = timedelta(minutes=10)
OTP_MAX_ATTEMPTS = 5


@api_view(["POST"])
def signup(request):
    serializer = SignupSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    user = serializer.save()

    return Response(
        {
            "message": (
                "Account created. Please request an OTP "
                "to verify your email address."
            ),
            "username": user.username,
            "email": user.email,
        },
        status=status.HTTP_201_CREATED,
    )


@api_view(["POST"])
def send_otp(request):
    username = str(request.data.get("username", "")).strip()

    if not username:
        return Response(
            {"error": "Username is required."},
            status=status.HTTP_400_BAD_REQUEST,
        )

    user = User.objects.filter(username=username).first()

    if user is None:
        return Response(
            {"error": "Account not found. Please sign up first."},
            status=status.HTTP_404_NOT_FOUND,
        )

    if user.is_verified:
        return Response(
            {"message": "This account is already verified."},
            status=status.HTTP_200_OK,
        )

    if not user.email:
        return Response(
            {"error": "No email address is registered for this account."},
            status=status.HTTP_400_BAD_REQUEST,
        )

    otp = str(secrets.randbelow(900000) + 100000)

    # Delete and recreate the record so the expiry clock resets on resend.
    EmailVerification.objects.filter(user=user).delete()
    EmailVerification.objects.create(user=user, otp=otp)

    try:
        send_mail(
            subject="Your ShopZone verification code",
            message=(
                f"Hello {user.username},\n\n"
                f"Your ShopZone verification code is {otp}.\n"
                "It expires in 10 minutes. Do not share this code.\n"
            ),
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[user.email],
            fail_silently=False,
        )
    except Exception:
        # Do not reveal the OTP in the response if email delivery fails.
        EmailVerification.objects.filter(user=user).delete()
        return Response(
            {
                "error": (
                    "We could not send your verification email. "
                    "Please check the email configuration and try again."
                )
            },
            status=status.HTTP_503_SERVICE_UNAVAILABLE,
        )

    return Response(
        {"message": "Verification code sent to your registered email."},
        status=status.HTTP_200_OK,
    )


@api_view(["POST"])
def verify_otp(request):
    username = str(request.data.get("username", "")).strip()
    otp = str(request.data.get("otp", "")).strip()

    if not username or not otp:
        return Response(
            {"error": "Username and OTP are required."},
            status=status.HTTP_400_BAD_REQUEST,
        )

    user = User.objects.filter(username=username).first()

    if user is None:
        return Response(
            {"error": "Invalid verification request."},
            status=status.HTTP_400_BAD_REQUEST,
        )

    verification = EmailVerification.objects.filter(user=user).first()

    if verification is None:
        return Response(
            {"error": "No active OTP was found. Please request a new one."},
            status=status.HTTP_400_BAD_REQUEST,
        )

    if timezone.now() - verification.created_at > OTP_LIFETIME:
        verification.delete()
        return Response(
            {"error": "Your OTP has expired. Please request a new one."},
            status=status.HTTP_400_BAD_REQUEST,
        )

    if verification.attempts >= OTP_MAX_ATTEMPTS:
        verification.delete()
        return Response(
            {"error": "Too many attempts. Please request a new OTP."},
            status=status.HTTP_429_TOO_MANY_REQUESTS,
        )

    if not secrets.compare_digest(verification.otp, otp):
        verification.attempts += 1
        verification.save(update_fields=["attempts"])

        if verification.attempts >= OTP_MAX_ATTEMPTS:
            verification.delete()
            return Response(
                {"error": "Too many attempts. Please request a new OTP."},
                status=status.HTTP_429_TOO_MANY_REQUESTS,
            )

        return Response(
            {"error": "Incorrect OTP."},
            status=status.HTTP_400_BAD_REQUEST,
        )

    user.is_verified = True
    user.save(update_fields=["is_verified"])
    verification.delete()

    return Response(
        {"message": "Email verified successfully."},
        status=status.HTTP_200_OK,
    )


@api_view(["POST"])
def login_view(request):
    username = str(request.data.get("username", "")).strip()
    password = request.data.get("password", "")

    if not username or not password:
        return Response(
            {"error": "Username and password are required."},
            status=status.HTTP_400_BAD_REQUEST,
        )

    user = authenticate(request, username=username, password=password)

    if user is None:
        return Response(
            {"error": "Invalid username or password."},
            status=status.HTTP_401_UNAUTHORIZED,
        )

    if not user.is_verified:
        return Response(
            {"error": "Please verify your email before logging in."},
            status=status.HTTP_403_FORBIDDEN,
        )

    refresh = RefreshToken.for_user(user)

    return Response({
        "access": str(refresh.access_token),
        "refresh": str(refresh),
        "user": UserSerializer(user).data,
    })


@api_view(["GET"])
@permission_classes([IsVerifiedUser])
def profile(request):
    return Response(UserSerializer(request.user).data)


@api_view(["POST"])
@permission_classes([IsAuthenticated])
def logout_view(request):
    refresh_token = request.data.get("refresh")

    if not refresh_token:
        return Response(
            {"error": "Refresh token is required."},
            status=status.HTTP_400_BAD_REQUEST,
        )

    try:
        RefreshToken(refresh_token).blacklist()
    except TokenError:
        return Response(
            {"error": "Invalid or expired refresh token."},
            status=status.HTTP_400_BAD_REQUEST,
        )

    return Response(status=status.HTTP_204_NO_CONTENT)
