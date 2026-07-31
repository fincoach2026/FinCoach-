from django.urls import path
from . import views

app_name = "tracker"

urlpatterns = [
	path("api/summary/", views.api_summary, name="api_summary"),
	path("api/transaction/", views.api_record_transaction, name="api_transaction"),
	path("", views.dashboard_page, name="dashboard"),
]
