from django.http import JsonResponse, HttpResponse
from django.views.decorators.csrf import csrf_exempt
import json


def monthly_payment(principal, annual_rate_pct, months):
	if months <= 0:
		return 0
	monthly_rate = (annual_rate_pct / 100) / 12
	if monthly_rate == 0:
		return principal / months
	return principal * (monthly_rate * (1 + monthly_rate) ** months) / ((1 + monthly_rate) ** months - 1)


def helper_page(request):
	# Simple page fallback if someone visits the helper in a browser
	return HttpResponse("Financial Helper API is available at /helper/api/advice/")


@csrf_exempt
def api_advice(request):
	"""Accepts POST JSON with purchase details and budget, returns a math-based verdict."""
	if request.method != "POST":
		return JsonResponse({"error": "POST required"}, status=405)
	try:
		body = json.loads(request.body or "{}")
	except Exception:
		return JsonResponse({"error": "invalid json"}, status=400)

	price = float(body.get("price", 0))
	down_payment = float(body.get("down_payment", 0))
	rate = float(body.get("rate", 0))
	term_months = int(body.get("term_months", 60))
	income = float(body.get("income", 3000))
	commitments = float(body.get("commitments", 1500))

	loan_amount = max(price - down_payment, 0)
	payment = monthly_payment(loan_amount, rate, term_months)
	total_cost = payment * term_months + down_payment
	budget_after = income - commitments - payment
	ratio = payment / income if income > 0 else 1

	if ratio > 0.20 or budget_after < 0:
		verdict = "stretch"
	elif ratio > 0.12:
		verdict = "manageable"
	else:
		verdict = "comfortable"

	return JsonResponse({
		"payment": round(payment, 2),
		"total_cost": round(total_cost, 2),
		"budget_after": round(budget_after, 2),
		"ratio": round(ratio, 4),
		"verdict": verdict,
	})
