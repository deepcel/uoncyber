from django.urls import path

from .views import (
    RegisterView,
    Generate2FAView,
    GenerateQRCodeView,
    Verify2FAView,
    LoginView,
    MFALoginView,
)

urlpatterns = [
    path("register/", RegisterView.as_view(), name="register"),

    path("login/", LoginView.as_view(), name="login"),

    path("login/2fa/", MFALoginView.as_view(), name="login-2fa"),

    path("2fa/setup/", Generate2FAView.as_view(), name="2fa-setup"),

    path("2fa/qr/", GenerateQRCodeView.as_view(), name="2fa-qr"),

    path("2fa/verify/", Verify2FAView.as_view(), name="2fa-verify"),
]