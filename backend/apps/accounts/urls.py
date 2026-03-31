from django.urls import path
from rest_framework_simplejwt.views import TokenRefreshView

from . import views


urlpatterns = [
    path("login/", views.EmailOrPhoneLoginView.as_view(), name="login"),
    path("refresh/", TokenRefreshView.as_view(), name="token-refresh"),
    path("me/", views.CurrentUserView.as_view(), name="me"),
    path("dashboard/", views.DashboardSummaryView.as_view(), name="dashboard"),
    path("users/", views.UserManagementView.as_view(), name="user-management"),
]
