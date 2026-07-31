from django.contrib import admin
from .models import AdviceRequest


@admin.register(AdviceRequest)
class AdviceRequestAdmin(admin.ModelAdmin):
	list_display = ("id", "user", "verdict", "payment", "created_at")
	list_filter = ("verdict", "created_at")
	readonly_fields = ("created_at",)
