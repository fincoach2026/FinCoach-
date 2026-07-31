from django.http import JsonResponse, HttpResponse
from django.views.decorators.csrf import csrf_exempt
import json


def dashboard_page(request):
	return HttpResponse("Tracker API is available at /tracker/api/summary/")


def _sample_summary():
	return {
		"checking": 1200.0,
		"savings": 3500.0,
		"investments": 1500.0,
		"credit_debt": 400.0,
		"loans": 8000.0,
	}


def api_summary(request):
	# For now return a sample summary. Later this should read from the DB.
	return JsonResponse(_sample_summary())


@csrf_exempt
def api_record_transaction(request):
	if request.method != "POST":
		return JsonResponse({"error": "POST required"}, status=405)
	try:
		body = json.loads(request.body or "{}")
	except Exception:
		return JsonResponse({"error": "invalid json"}, status=400)

	# Echo back what was submitted for now. A real implementation would persist this.
	return JsonResponse({"ok": True, "transaction": body})
