"""Admin configuration for the products app."""

from django.contrib import admin
from .models import Product


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    """Admin interface configuration for Product model."""
    list_display = ['id', 'name', 'price', 'category',
                    'stock', 'is_active', 'created_at']
    list_filter = ['category', 'is_active', 'created_at']
    search_fields = ['name', 'description']
    list_editable = ['price', 'is_active', 'stock']
    list_per_page = 20
    date_hierarchy = 'created_at'

    fieldsets = (
        ('Main Information', {
            'fields': ('name', 'description', 'price', 'category')
        }),
        ('Inventory', {
            'fields': ('stock', 'unit', 'is_active')
        }),
        ('Image', {
            'fields': ('image_path',)
        }),
        ('Dates', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )

    readonly_fields = ['created_at', 'updated_at', 'views_count']

    actions = ['make_active', 'make_inactive', 'reset_views_count']

    def make_active(self, request, queryset):
        updated = queryset.update(is_active=True)
        self.message_user(request, f'{updated} products marked as active.')

    make_active.short_description = "Mark selected products as active"

    def make_inactive(self, request, queryset):
        updated = queryset.update(is_active=False)
        self.message_user(request, f'{updated} products marked as inactive.')

    make_inactive.short_description = "Mark selected products as inactive"

    def reset_views_count(self, request, queryset):
        updated = queryset.update(views_count=0)
        self.message_user(
            request, f'Views count reset for {updated} products.')

    reset_views_count.short_description = "Reset views count"
