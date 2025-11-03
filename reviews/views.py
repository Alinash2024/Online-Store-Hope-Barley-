"""Views for the reviews app."""

from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.exceptions import ValidationError
from products.models import Product
from .models import Review
from .forms import ReviewForm


@login_required
def add_review(request, product_id):
    """Add a review for a specific product.

    Args:
        request: The HTTP request object.
        product_id: The ID of the product to review.

    Returns:
        HttpResponse: The rendered add review form or redirects after
                      successful creation or handling errors.
    """
    product = get_object_or_404(Product, id=product_id)

    existing_review = Review.objects.filter(
        product=product, user=request.user).first()

    if existing_review:
        messages.info(request,
                      'You have already reviewed this product.')

        if product_id == 11:
            return redirect('products:product_detail_unmalted_wheat')
        elif product_id == 13:
            return redirect('products:product_detail_west_coast_ipa_kit')
        else:
            return redirect('products:product_detail_unmalted_wheat')

    if request.method == 'POST':
        form = ReviewForm(request.POST)
        if form.is_valid():
            try:
                review = form.save(commit=False)
                review.product = product
                review.user = request.user

                try:
                    review.validate_user_purchase()
                    review.save()
                    messages.success(
                        request, 'Review added successfully!'
                    )
                    if product_id == 11:
                        return redirect(
                            'products:product_detail_unmalted_wheat'
                        )
                    elif product_id == 13:
                        return redirect(
                            'products:product_detail_west_coast_ipa_kit'
                        )
                    else:
                        return redirect(
                            'products:product_detail_unmalted_wheat'
                        )
                except ValidationError as e:
                    messages.error(request, str(e))

            except Exception as e:
                messages.error(
                    request,
                    f'Error adding review: {str(e)}'
                )
        else:
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(
                        request, f'Error in field {field}: {error}'
                    )
    else:
        form = ReviewForm()

    return render(
        request, 'reviews/add_review.html',
        {
            'form': form,
            'product': product
        }
    )
