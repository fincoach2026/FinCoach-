from django.contrib import admin
from .models import Transaction


@admin.register(Transaction)
class TransactionAdmin(admin.ModelAdmin):
	list_display = ("id", "user", "amount", "category", "occurred_at")
	list_filter = ("category", "occurred_at")
	search_fields = ("description",)
