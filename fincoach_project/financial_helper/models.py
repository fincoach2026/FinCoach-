from django.db import models
from django.conf import settings


class AdviceRequest(models.Model):
	user = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, blank=True, on_delete=models.SET_NULL)
	price = models.DecimalField(max_digits=12, decimal_places=2, default=0)
	down_payment = models.DecimalField(max_digits=12, decimal_places=2, default=0)
	rate = models.FloatField(default=0)
	term_months = models.IntegerField(default=60)
	income = models.DecimalField(max_digits=12, decimal_places=2, default=0)
	commitments = models.DecimalField(max_digits=12, decimal_places=2, default=0)
	verdict = models.CharField(max_length=32, blank=True)
	payment = models.DecimalField(max_digits=12, decimal_places=2, default=0)
	created_at = models.DateTimeField(auto_now_add=True)

	def __str__(self):
		return f"AdviceRequest #{self.id} - {self.verdict}"
