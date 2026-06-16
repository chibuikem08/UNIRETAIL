def cart_count(request):
    """Inject cart item count into every template context."""
    count = 0
    if request.user.is_authenticated and hasattr(request.user, 'can_shop') and request.user.can_shop:
        try:
            count = request.user.cart.item_count
        except Exception:
            count = 0
    return {'cart_item_count': count}
