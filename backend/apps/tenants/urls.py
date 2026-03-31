from django.urls import path

from . import views


urlpatterns = [
    path("", views.TenantListCreateView.as_view(), name="tenant-list-create"),
    path("activation/verify/", views.VerifyTenantOtpView.as_view(), name="tenant-activation-verify"),
    path("activation/complete/", views.CompleteTenantActivationView.as_view(), name="tenant-activation-complete"),
    path("<int:tenant_id>/otp/", views.TenantOtpDetailView.as_view(), name="tenant-otp-detail"),
]

