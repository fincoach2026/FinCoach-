from django.db import models
from django.conf import settings


class Transaction(models.Model):
	user = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, blank=True, on_delete=models.SET_NULL)
	amount = models.DecimalField(max_digits=12, decimal_places=2)
	category = models.CharField(max_length=64, blank=True)
	description = models.TextField(blank=True)
	occurred_at = models.DateTimeField()
	created_at = models.DateTimeField(auto_now_add=True)

	def __str__(self):
		return f"{self.occurred_at.date()} {self.amount} {self.category}"
