"""Admin configuration for the payments app."""

from django.contrib import admin
from .models import Payment, PaymentMethod, Refund


class RefundInline(admin.TabularInline):
    """Inline admin for Refund model associated with Payment."""
    model = Refund
    extra = 0
    readonly_fields = ["created_at", "updated_at", "processed_at"]
    fields = ["amount", "reason", "status", "created_at", "processed_at"]


@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    """Admin interface configuration for Payment model."""
    list_display = [
        "id",
        "order",
        "user",
        "amount",
        "payment_method",
        "status",
        "transaction_id",
        "created_at",
    ]
    list_filter = ["status", "payment_method", "created_at", "updated_at"]
    search_fields = [
        "id",
        "order__id",
        "transaction_id",
        "user__email",
        "user__username",
    ]
    readonly_fields = ["created_at", "updated_at", "payment_date"]
    list_per_page = 20
    inlines = [RefundInline]

    list_select_related = ["order", "user"]

    actions = [
        "mark_as_completed",
        "mark_as_failed",
        "mark_as_pending",
        "mark_as_refunded",
        "mark_as_cancelled",
    ]

    fieldsets = (
        (
            "Основная информация",
            {"fields": ("order", "user", "amount", "payment_method")},
        ),
        (
            "Статус и даты",
            {
                "fields": (
                    "status",
                    "transaction_id",
                    "payment_date",
                    "created_at",
                    "updated_at",
                )
            },
        ),
        (
            "Детали",
            {"fields": ("gateway_response",), "classes": ("collapse",)},
        ),
    )

    def mark_as_completed(self, request, queryset):
        updated = queryset.update(status="completed")
        self.message_user(
            request, f"{updated} платежей отмечены как завершенные."
        )

    mark_as_completed.short_description = "Отметить как завершенные"

    def mark_as_failed(self, request, queryset):
        updated = queryset.update(status="failed")
        self.message_user(
            request, f"{updated} платежей отмечены как неудачные."
        )

    mark_as_failed.short_description = "Отметить как неудачные"

    def mark_as_pending(self, request, queryset):
        updated = queryset.update(status="pending")
        self.message_user(
            request, f"{updated} платежей отмечены как ожидающие."
        )

    mark_as_pending.short_description = "Отметить как ожидающие"

    def mark_as_refunded(self, request, queryset):
        updated = queryset.update(status="refunded")
        self.message_user(
            request, f"{updated} платежей отмечены как возвращенные."
        )

    mark_as_refunded.short_description = "Отметить как возвращенные"

    def mark_as_cancelled(self, request, queryset):
        updated = queryset.update(status="cancelled")
        self.message_user(
            request, f"{updated} платежей отмечены как отмененные."
        )

    mark_as_cancelled.short_description = "Отметить как отмененные"


@admin.register(PaymentMethod)
class PaymentMethodAdmin(admin.ModelAdmin):
    """Admin interface configuration for PaymentMethod model."""
    list_display = ["name", "is_active", "created_at"]
    list_filter = ["is_active", "created_at"]
    search_fields = ["name", "description"]
    list_per_page = 20

    fieldsets = (
        (
            "Основная информация",
            {"fields": ("name", "description", "is_active")},
        ),
        (
            "Даты",
            {"fields": ("created_at", "updated_at"), "classes": ("collapse",)},
        ),
    )

    readonly_fields = ["created_at", "updated_at"]


@admin.register(Refund)
class RefundAdmin(admin.ModelAdmin):
    """Admin interface configuration for Refund model."""
    list_display = ["id", "payment", "amount", "status", "created_at"]
    list_filter = ["status", "created_at", "processed_at"]
    search_fields = [
        "id",
        "payment__id",
        "payment__order__id",
        "payment__transaction_id",
    ]
    list_per_page = 20

    fieldsets = (
        ("Основная информация", {"fields": ("payment", "amount", "reason")}),
        (
            "Статус и даты",
            {"fields": ("status", "created_at", "updated_at", "processed_at")},
        ),
    )

    readonly_fields = ["created_at", "updated_at", "processed_at"]

    actions = ["mark_as_completed", "mark_as_failed", "mark_as_processing"]

    def mark_as_completed(self, request, queryset):
        updated = queryset.update(status="completed")
        self.message_user(
            request, f"{updated} возвратов отмечены как завершенные."
        )

    mark_as_completed.short_description = "Отметить как завершенные"

    def mark_as_failed(self, request, queryset):
        updated = queryset.update(status="failed")
        self.message_user(
            request, f"{updated} возвратов отмечены как неудачные."
        )

    mark_as_failed.short_description = "Отметить как неудачные"

    def mark_as_processing(self, request, queryset):
        updated = queryset.update(status="processing")
        self.message_user(
            request, f"{updated} возвратов отмечены как обрабатываемые."
        )

    mark_as_processing.short_description = "Отметить как обрабатываемые"
