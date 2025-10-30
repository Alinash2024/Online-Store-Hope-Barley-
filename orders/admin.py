"""Admin configuration for the orders app.

This module defines the admin interfaces for the Order and OrderItem models.
It includes:
- Custom display fields and filters for the admin list views
- Inline editing for OrderItems within the Order admin page
- Bulk actions for updating order statuses
- Custom methods for calculating and displaying order metrics
- Integration with custom analytics views
"""

from django.contrib import admin
from django.urls import path, reverse
from django.db.models import Sum
from .models import Order, OrderItem
from . import views


class OrderItemInline(admin.TabularInline):
    """Inline admin interface for OrderItem model.

    Allows editing OrderItem objects directly within the Order admin page.
    Uses raw_id_fields for the product to avoid performance issues with
    large product catalogs.
    """

    model = OrderItem
    raw_id_fields = ['product']
    extra = 0


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    """Admin interface for the Order model.

    Provides a comprehensive admin view for managing orders, including:
    - Display of key order information (ID, user, total price, status, etc.)
    - Filtering and searching capabilities
    - Inline editing of associated OrderItems
    - Bulk actions for updating order statuses
    - Custom methods for calculating metrics like item count and revenue
    - Integration with custom analytics views
    """

    list_display = [
        'id',
        'user',
        'total_price',
        'is_paid',
        'status',
        'created_at',
        'get_items_count',
        'get_revenue'
    ]
    list_filter = ['is_paid', 'status', 'created_at']
    search_fields = ['user__email', 'id']
    readonly_fields = ['created_at', 'updated_at']
    inlines = [OrderItemInline]
    list_per_page = 20
    list_select_related = ['user']

    actions = [
        'mark_as_paid',
        'mark_as_processing',
        'mark_as_shipped',
        'mark_as_delivered',
        'mark_as_cancelled'
    ]

    def get_items_count(self, obj):
        return obj.items.aggregate(total=Sum('quantity'))['total'] or 0

    get_items_count.short_description = 'Items Count'
    get_items_count.admin_order_field = 'items__quantity'

    def get_revenue(self, obj):
        return obj.get_revenue()

    get_revenue.short_description = 'Revenue'
    get_revenue.admin_order_field = 'total_price'

    def mark_as_paid(self, request, queryset):
        updated = queryset.update(is_paid=True)
        self.message_user(
            request,
            f'{updated} orders marked as paid.'
        )

    mark_as_paid.short_description = "Mark as paid"

    def mark_as_processing(self, request, queryset):
        updated = queryset.update(status='processing')
        self.message_user(
            request,
            f'{updated} orders marked as processing.'
        )

    mark_as_processing.short_description = "Mark as processing"

    def mark_as_shipped(self, request, queryset):
        updated = queryset.update(status='shipped')
        self.message_user(
            request,
            f'{updated} orders marked as shipped.'
        )

    mark_as_shipped.short_description = "Mark as shipped"

    def mark_as_delivered(self, request, queryset):
        updated = queryset.update(status='delivered')
        self.message_user(
            request,
            f'{updated} orders marked as delivered.'
        )

    mark_as_delivered.short_description = "Mark as delivered"

    def mark_as_cancelled(self, request, queryset):
        updated = queryset.update(status='cancelled')
        self.message_user(
            request,
            f'{updated} orders marked as cancelled.'
        )

    mark_as_cancelled.short_description = "Mark as cancelled"

    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path(
                'orders-analytics/',
                self.admin_site.admin_view(views.admin_order_analytics),
                name='orders-analytics'
            ),
        ]
        return custom_urls + urls

    def changelist_view(self, request, extra_context=None):
        extra_context = extra_context or {}
        extra_context['analytics_url'] = reverse('admin:orders-analytics')
        return super().changelist_view(request, extra_context)


@admin.register(OrderItem)
class OrderItemAdmin(admin.ModelAdmin):
    """Admin interface for the OrderItem model.

    Provides an admin view for managing individual items within orders:
    - Display of key item information (order, product, quantity, price)
    - Filtering and searching capabilities
    - Custom methods for calculating metrics like total price, revenue, profit
    """

    list_display = [
        'order',
        'product',
        'quantity',
        'price',
        'get_total_price',
        'get_revenue',
        'get_profit'
    ]
    list_filter = ['order__created_at', 'order__status']
    search_fields = ['order__id', 'product__name']
    list_per_page = 20

    def get_total_price(self, obj):
        return obj.get_total_price()

    get_total_price.short_description = 'Total Price'
    get_total_price.admin_order_field = 'quantity'

    def get_revenue(self, obj):
        return obj.revenue

    get_revenue.short_description = 'Revenue'
    get_revenue.admin_order_field = 'quantity'

    def get_profit(self, obj):
        if not obj.product or obj.product.cost is None:
            return 0
        try:
            return (obj.price - obj.product.cost) * obj.quantity
        except (TypeError, ValueError):
            return 0

    get_profit.short_description = 'Profit'
