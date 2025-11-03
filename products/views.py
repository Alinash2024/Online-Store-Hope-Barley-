"""Views for the products app."""

from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Q
from django.core.paginator import Paginator
from django.http import HttpResponseNotAllowed
from .models import Product


def product_list(request):
    """Display a list of products with filtering and pagination.

    Args:
        request: The HTTP request object.

    Returns:
        HttpResponse: The rendered product list page.
    """
    products = Product.objects.filter(is_active=True)

    search_query = request.GET.get('search', '')
    min_price = request.GET.get('min_price', '')
    max_price = request.GET.get('max_price', '')
    stock_filter = request.GET.get('stock', '')
    sort_by = request.GET.get('sort', 'name')

    if search_query:
        products = products.filter(
            Q(name__icontains=search_query) |
            Q(description__icontains=search_query)
        )

    if min_price:
        products = products.filter(price__gte=min_price)

    if max_price:
        products = products.filter(price__lte=max_price)

    if stock_filter:
        products = products.filter(stock__gte=stock_filter)

    if sort_by == 'price_asc':
        products = products.order_by('price')
    elif sort_by == 'price_desc':
        products = products.order_by('-price')
    elif sort_by == 'created_at':
        products = products.order_by('-created_at')
    elif sort_by == 'stock':
        products = products.order_by('-stock')
    else:
        products = products.order_by('name')

    paginator = Paginator(products, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    context = {
        'products': page_obj,
        'search_query': search_query,
        'min_price': min_price,
        'max_price': max_price,
        'stock_filter': stock_filter,
        'sort_by': sort_by,
    }

    return render(request, 'products/products.html', context)


def product_detail(request, pk):
    """Display detailed information about a specific product.

    Args:
        request: The HTTP request object.
        pk: The primary key of the product.

    Returns:
        HttpResponse: The rendered product detail page.
    """
    product = get_object_or_404(Product, pk=pk)

    product.views_count += 1
    product.save()

    template_mapping = {
        1: 'products/product-caramel-malt.html',
        2: 'products/product-cascade-hops.html',
        4: 'products/product-centennial-hops.html',
        5: 'products/product-citra-hops.html',
        6: 'products/product-imperial-yeast.html',
        7: 'products/product-maris-otter-malt.html',
        8: 'products/product-mosaic-hops.html',
        9: 'products/product-pilsner-malt.html',
        10: 'products/product-saaz-hops.html',
        11: 'products/product-safale-us05-yeast.html',
        12: 'products/product-unmalted-wheat.html',
        13: 'products/product-west-coast-ipa-kit.html',
    }

    template_name = template_mapping.get(
        product.id,
        'products/product_detail.html'
    )
    context = {
        'product': product,
    }

    return render(request, template_name, context)


@login_required
def add_product(request):
    """Create a new product.

    Args:
        request: The HTTP request object.

    Returns:
        HttpResponse: The rendered add product form or redirects after
                      successful creation.
    """
    if request.method == 'POST':
        name = request.POST.get('name')
        description = request.POST.get('description')
        price = request.POST.get('price')
        stock = request.POST.get('stock', 0)
        is_active = bool(request.POST.get('is_active'))
        unit = request.POST.get('unit', 'item')

        if name and price:
            Product.objects.create(
                name=name,
                description=description,
                price=price,
                stock=stock,
                is_active=is_active,
                unit=unit
            )
            messages.success(
                request, f'Product "{name}" created successfully!')
            return redirect('products:list')
        else:
            messages.error(request, 'Please fill in all required fields.')

    return render(request, 'products/add.html')


@login_required
def product_update(request, pk):
    """Update information about a product.

    Args:
        request: The HTTP request object.
        pk: The primary key of the product to update.

    Returns:
        HttpResponse: The rendered update product form or redirects after
                      successful update.
    """
    product = get_object_or_404(Product, pk=pk)

    if request.method == 'POST':
        product.name = request.POST.get('name', product.name)
        product.description = request.POST.get('description',
                                               product.description)
        product.price = request.POST.get('price', product.price)
        product.stock = request.POST.get('stock', product.stock)
        product.is_active = bool(request.POST.get('is_active',
                                                  product.is_active))
        product.unit = request.POST.get('unit', product.unit)

        product.save()
        messages.success(
            request, f'Product "{product.name}" updated successfully!')
        return redirect('products:list')

    context = {
        'product': product,
    }

    return render(request, 'products/add.html', context)


@login_required
def product_delete(request, pk):
    """Delete a product without confirmation via a separate template.

    Args:
        request: The HTTP request object (must be POST).
        pk: The primary key of the product to delete.

    Returns:
        HttpResponse: Redirects to the product list page after deletion.
    """
    if request.method != 'POST':
        return HttpResponseNotAllowed(['POST'])

    product = get_object_or_404(Product, pk=pk)
    product_name = product.name
    product.delete()
    messages.success(
        request, f'Product "{product_name}" deleted successfully!')
    return redirect('products:list')


def dashboard(request):
    """Display a dashboard with product analytics.

    Args:
        request: The HTTP request object.

    Returns:
        HttpResponse: The rendered dashboard page.
    """
    total_products = Product.objects.count()
    active_products = Product.objects.filter(is_active=True).count()
    out_of_stock = Product.objects.filter(stock=0).count()

    recent_products = Product.objects.order_by('-created_at')[:5]

    popular_products = Product.objects.order_by('-views_count')[:5]

    context = {
        'total_products': total_products,
        'active_products': active_products,
        'out_of_stock': out_of_stock,
        'recent_products': recent_products,
        'popular_products': popular_products,
    }

    return render(request, 'products/dashboard.html', context)
