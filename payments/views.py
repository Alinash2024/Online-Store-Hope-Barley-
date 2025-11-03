"""Views for the payments app.

This module defines views for processing payments, handling webhooks,
managing refunds, and displaying payment history for users.
"""

from django.shortcuts import get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
from django.contrib import messages
from django.db import transaction
from django.utils import timezone
import json
import uuid
from .models import Payment, Refund
from orders.models import Order


@login_required
def payment_process(request, order_id):
    """Process payment for an order.

    Handles both GET (display payment form) and POST (process payment)
    requests for a specific order.

    Args:
        request: The HTTP request object.
        order_id: The ID of the order to process payment for.

    Returns:
        HttpResponse: The rendered payment form or redirects based on
                      payment status.
    """
    order = get_object_or_404(
        Order, id=order_id, user=request.user, status="pending"
    )

    payment, created = Payment.objects.get_or_create(
        order=order,
        defaults={
            "user": request.user,
            "amount": order.total_price,
            "payment_method": order.payment_method,
            "status": "pending",
        },
    )

    if not created and payment.status != "pending":
        if payment.status == "completed":
            messages.info(request, "Payment has already been "
                                   "processed successfully.")
            return redirect("orders:order_success", order_id=order.id)
        elif payment.status == "failed":
            messages.error(
                request,
                "Previous payment attempt failed. Please try again.",
            )

    if request.method == "POST":
        payment_method = request.POST.get(
            "payment_method", order.payment_method
        )
        card_number = request.POST.get("card_number", "")
        expiry_date = request.POST.get("expiry_date", "")
        cvv = request.POST.get("cvv", "")

        errors = []
        if payment_method in ["credit_card", "debit_card"]:
            if not card_number or len(card_number.replace(" ", "")) < 16:
                errors.append("Invalid card number")
            if not expiry_date:
                errors.append("Please enter expiry date")
            if not cvv or len(cvv) < 3:
                errors.append("Please enter CVV code")

        if errors:
            for error in errors:
                messages.error(request, error)
            return render(
                request,
                "payments/payment_form.html",
                {
                    "order": order,
                    "payment": payment,
                },
            )

        try:
            with transaction.atomic():
                transaction_id = (
                    str(uuid.uuid4()).replace("-", "")[:20].upper()
                )

                payment.transaction_id = transaction_id
                payment.payment_method = payment_method
                payment.status = "completed"
                payment.payment_date = timezone.now()
                payment.gateway_response = json.dumps(
                    {
                        "status": "success",
                        "message": "Payment processed successfully",
                        "transaction_id": transaction_id,
                    }
                )
                payment.save()

                order.is_paid = True
                order.status = "processing"
                order.save()

            messages.success(request, "Payment processed successfully!")
            return redirect("orders:order_success", order_id=order.id)

        except Exception as e:
            payment.status = "failed"
            payment.gateway_response = json.dumps(
                {"status": "error", "message": str(e)}
            )
            payment.save()

            messages.error(
                request,
                "An error occurred processing the payment. Please try again.",
            )
            return render(
                request,
                "payments/payment_form.html",
                {
                    "order": order,
                    "payment": payment,
                },
            )

    return render(
        request,
        "payments/payment_form.html",
        {
            "order": order,
            "payment": payment,
        },
    )


@login_required
def payment_detail(request, payment_id):
    """Display details for a specific payment.

    Args:
        request: The HTTP request object.
        payment_id: The ID of the payment to retrieve details for.

    Returns:
        HttpResponse: The rendered payment detail page.
    """
    payment = get_object_or_404(Payment, id=payment_id, user=request.user)

    gateway_response = None
    if payment.gateway_response:
        try:
            gateway_response = json.loads(payment.gateway_response)
        except json.JSONDecodeError:
            gateway_response = {"error": "Invalid response format"}

    return render(
        request,
        "payments/payment_detail.html",
        {"payment": payment, "gateway_response": gateway_response},
    )


@login_required
def request_refund(request, payment_id):
    """Handle refund request for a completed payment.

    Args:
        request: The HTTP request object.
        payment_id: The ID of the payment to request a refund for.

    Returns:
        HttpResponse: The rendered refund request form or redirects after
                      processing the request.
    """
    payment = get_object_or_404(
        Payment, id=payment_id, user=request.user, status="completed"
    )

    if request.method == "POST":
        reason = request.POST.get("reason", "").strip()

        if not reason:
            messages.error(request, "Please provide a reason for the refund.")
            return render(
                request, "payments/refund_request.html",
                {"payment": payment}
            )

        try:
            Refund.objects.create(
                payment=payment,
                amount=payment.amount,
                reason=reason,
                status="requested",
            )

            payment.status = "refunded"
            payment.save()

            messages.success(
                request, "Refund request submitted successfully."
            )
            return redirect("payments:payment_detail", payment_id=payment.id)

        except Exception:
            messages.error(
                request, "An error occurred while creating the refund request."
            )
            return render(
                request, "payments/refund_request.html",
                {"payment": payment}
            )

    return render(
        request, "payments/refund_request.html", {"payment": payment}
    )


@csrf_exempt
@require_POST
def payment_webhook(request):
    """Webhook endpoint for processing payment gateway notifications.

    Args:
        request: The HTTP request object (POST, CSRF exempt).

    Returns:
        HttpResponse: Status 200 on success, 400 on error.
    """
    try:
        payload = json.loads(request.body)
        event_type = payload.get("event_type")
        transaction_id = payload.get("transaction_id")

        payment = get_object_or_404(Payment, transaction_id=transaction_id)

        if event_type == "payment.completed":
            with transaction.atomic():
                payment.status = "completed"
                payment.payment_date = timezone.now()
                payment.gateway_response = json.dumps(payload)
                payment.save()

                payment.order.is_paid = True
                payment.order.status = "processing"
                payment.order.save()

        elif event_type == "payment.failed":
            payment.status = "failed"
            payment.gateway_response = json.dumps(payload)
            payment.save()

        elif event_type == "payment.refunded":
            payment.status = "refunded"
            payment.gateway_response = json.dumps(payload)
            payment.save()

            payment.order.status = "cancelled"
            payment.order.save()

        return HttpResponse(status=200)

    except Exception:
        return HttpResponse(status=400)


@login_required
def payment_history(request):
    """Display payment history for the current user.

    Args:
        request: The HTTP request object.

    Returns:
        HttpResponse: The rendered payment history page.
    """
    payments = (
        Payment.objects.filter(user=request.user)
        .select_related("order")
        .order_by("-created_at")
    )

    return render(
        request, "payments/payment_history.html",
        {"payments": payments}
    )


def payment_cancel(request, payment_id):
    """Cancel a pending payment.

    Args:
        request: The HTTP request object.
        payment_id: The ID of the payment to cancel.

    Returns:
        HttpResponse: The rendered cancellation confirmation page or
                      redirects after processing.
    """
    payment = get_object_or_404(
        Payment, id=payment_id, user=request.user, status="pending"
    )

    if request.method == "POST":
        try:
            payment.status = "cancelled"
            payment.save()

            payment.order.status = "cancelled"
            payment.order.save()

            messages.success(request, "Payment cancelled successfully.")
            return redirect("payments:payment_history")

        except Exception:
            messages.error(request, "An error occurred the payment.")

    return render(
        request, "payments/payment_cancel.html",
        {"payment": payment}
    )


@login_required
def refund_detail(request, refund_id):
    """Display details for a specific refund.

    Args:
        request: The HTTP request object.
        refund_id: The ID of the refund to retrieve details for.

    Returns:
        HttpResponse: The rendered refund detail page.
    """
    refund = get_object_or_404(
        Refund, id=refund_id, payment__user=request.user
    )

    return render(request, "payments/refund_detail.html",
                  {"refund": refund})


@login_required
def refund_history(request):
    """Display refund history for the current user.

    Args:
        request: The HTTP request object.

    Returns:
        HttpResponse: The rendered refund history page.
    """
    refunds = (
        Refund.objects.filter(payment__user=request.user)
        .select_related("payment")
        .order_by("-created_at")
    )

    return render(
        request, "payments/refund_history.html",
        {"refunds": refunds}
    )
