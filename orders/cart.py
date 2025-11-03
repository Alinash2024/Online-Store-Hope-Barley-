"""Shopping cart implementation for the e-commerce application.

This module provides a Cart class that manages user's shopping cart items
using Django sessions. It allows adding, removing, and updating products
in the cart, calculating totals, and handling stock availability.
"""

from decimal import Decimal
from django.conf import settings
from products.models import Product


class Cart:
    """Manages the shopping cart using Django sessions.

    Provides methods to add, remove, and update items in the cart,
    calculate totals, and handle stock availability checks.
    """

    def __init__(self, request):
        """Initialize the cart."""
        self.session = request.session
        cart = self.session.get(settings.CART_SESSION_ID)
        if not cart:
            cart = self.session[settings.CART_SESSION_ID] = {}
        self.cart = cart

    def add(self, product, quantity=1, override_quantity=False):
        """Add a product to the cart or update its quantity."""
        product_id = str(product.id)
        if product_id not in self.cart:
            self.cart[product_id] = {
                'quantity': 0,
                'price': str(product.price)
            }
        if override_quantity:
            self.cart[product_id]['quantity'] = quantity
        else:
            self.cart[product_id]['quantity'] += quantity
        self.save()

    def save(self):
        self.session.modified = True

    def remove(self, product):
        """Remove a product from the cart."""
        product_id = str(product.id)
        if product_id in self.cart:
            del self.cart[product_id]
            self.save()

    def __iter__(self):
        """Iterate over the items, get products from the database."""
        product_ids = self.cart.keys()
        products = Product.objects.filter(id__in=product_ids)
        cart = self.cart.copy()
        for product in products:
            cart[str(product.id)]['product'] = product

        for item in cart.values():
            item['price'] = Decimal(item['price'])
            item['total_price'] = item['price'] * item['quantity']
            yield item

    def __len__(self):
        """Count all items in the cart."""
        return sum(item['quantity'] for item in self.cart.values())

    def get_total_price(self):
        """Calculate the total cost of the items in the cart."""
        return sum(
            Decimal(item['price']) * item['quantity']
            for item in self.cart.values()
        )

    def clear(self):
        del self.session[settings.CART_SESSION_ID]
        self.save()

    def get_cart_items(self):
        """Get all cart items."""
        return self.cart

    def clean_unavailable_items(self):
        """Remove items from the cart that are no longer available."""
        removed_items = []
        updated_items = []

        for product_id, item in self.cart.items():
            try:
                product = Product.objects.get(id=product_id)
                if product.stock <= 0:
                    removed_items.append({
                        'name': product.name,
                        'reason': 'out of stock'
                    })
                    del self.cart[product_id]
                elif item['quantity'] > product.stock:
                    updated_items.append({
                        'name': product.name,
                        'old_quantity': item['quantity'],
                        'new_quantity': product.stock
                    })
                    self.cart[product_id]['quantity'] = product.stock
            except Product.DoesNotExist:
                removed_items.append({
                    'name': f'Product ID {product_id}',
                    'reason': 'not found'
                })
                del self.cart[product_id]

        if removed_items or updated_items:
            self.save()

        return {
            'removed': removed_items,
            'updated': updated_items
        }
