from django.urls import path

from . import views


urlpatterns = [
    path("", views.PropertyListCreateView.as_view(), name="property-list-create"),
    path("<int:property_id>/assign-caretaker/", views.AssignCaretakerView.as_view(), name="assign-caretaker"),
]

