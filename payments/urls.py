"""URL patterns for the payments app."""

from django.urls import path
from . import views

app_name = "payments"

urlpatterns = [
    path(
        "process/<int:order_id>/",
        views.payment_process,
        name="payment_process",
    ),
    path(
        "detail/<int:payment_id>/", views.payment_detail, name="payment_detail"
    ),
    path("history/", views.payment_history, name="payment_history"),
    path(
        "cancel/<int:payment_id>/", views.payment_cancel, name="payment_cancel"
    ),
    path(
        "refund/request/<int:payment_id>/",
        views.request_refund,
        name="request_refund",
    ),
    path(
        "refund/detail/<int:refund_id>/",
        views.refund_detail,
        name="refund_detail",
    ),
    path("refund/history/", views.refund_history, name="refund_history"),
    path("webhook/", views.payment_webhook, name="payment_webhook"),
]
