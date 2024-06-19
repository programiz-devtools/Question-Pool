from django.urls import path

from .views import (
    RegisterView,
    CustomTokenObtainPairView,
    ForgetPasswordView,
    ResetPasswordView,
    VerifyOTPView,
    ResendOTPView,
    RegisterView,
    UpdateProfileFieldAPIView,
    LoginWithGoogle,
    CurrentOrganizationProfileAPIView,
    GetAdminProfileAPIView
)

urlpatterns = [
    path("login/", CustomTokenObtainPairView.as_view(), name="login"),
    path("google/login/", LoginWithGoogle.as_view(), name="login-with-google"),
    path("google/login/", LoginWithGoogle.as_view(), name="login-with-google"),
    path("resend-otp/", ResendOTPView.as_view(), name="resend-otp"),
    path("reset-password/", ResetPasswordView.as_view(), name="reset-password"),
    path("user-register/", RegisterView.as_view(), name="sign-up"),
    path("forget-password/", ForgetPasswordView.as_view(), name="forgot-password"),
    path("verify-otp/", VerifyOTPView.as_view(), name="verify-otp"),
    path('update-profile-field/', UpdateProfileFieldAPIView.as_view(), name='update_profile_field'),
    path("view-profile/", CurrentOrganizationProfileAPIView.as_view(), name="view-profile"),
     path("get-admin-details/", GetAdminProfileAPIView.as_view(), name="admin-view-profile"),
 
  
]
