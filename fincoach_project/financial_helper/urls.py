from django.urls import path
from . import views

app_name = "financial_helper"

urlpatterns = [
	path("api/advice/", views.api_advice, name="api_advice"),
	path("", views.helper_page, name="helper_page"),
]
