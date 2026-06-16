from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db import transaction
from shops.models import Product
from .models import Cart, CartItem, Order, OrderItem
from .forms import CheckoutForm


# ── Helpers ──────────────────────────────────────────────────────────────────

def get_or_create_cart(user):
    cart, _ = Cart.objects.get_or_create(user=user)
    return cart


def buyer_required(view_func):
    from functools import wraps
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect('accounts:login')
        if not request.user.can_shop:
            messages.error(request, 'Only students and staff can place orders.')
            return redirect('shops:home')
        return view_func(request, *args, **kwargs)
    return wrapper


def vendor_required(view_func):
    from functools import wraps
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect('accounts:login')
        if not (request.user.is_vendor and request.user.is_approved_vendor):
            messages.error(request, 'Vendor access only.')
            return redirect('shops:home')
        return view_func(request, *args, **kwargs)
    return wrapper


# ── Cart Views ────────────────────────────────────────────────────────────────

@buyer_required
def cart_view(request):
    cart       = get_or_create_cart(request.user)
    cart_items = cart.cart_items.select_related('product__shop').all()
    return render(request, 'orders/cart.html', {'cart': cart, 'cart_items': cart_items})


@buyer_required
def add_to_cart(request, product_pk):
    product = get_object_or_404(Product, pk=product_pk, is_available=True)

    if not product.in_stock:
        messages.error(request, f'"{product.name}" is out of stock.')
        return redirect(product.get_absolute_url())

    cart      = get_or_create_cart(request.user)
    cart_item, created = CartItem.objects.get_or_create(cart=cart, product=product)

    if not created:
        if cart_item.quantity < product.stock:
            cart_item.quantity += 1
            cart_item.save()
            messages.success(request, f'"{product.name}" quantity updated.')
        else:
            messages.warning(request, f'You\'ve reached the maximum stock for "{product.name}".')
    else:
        messages.success(request, f'"{product.name}" added to cart!')

    next_url = request.GET.get('next', 'orders:cart')
    return redirect(next_url)


@buyer_required
def remove_from_cart(request, item_pk):
    cart_item = get_object_or_404(CartItem, pk=item_pk, cart__user=request.user)
    name = cart_item.product.name
    cart_item.delete()
    messages.success(request, f'"{name}" removed from cart.')
    return redirect('orders:cart')


@buyer_required
def update_cart(request, item_pk):
    cart_item = get_object_or_404(CartItem, pk=item_pk, cart__user=request.user)
    try:
        qty = int(request.POST.get('quantity', 1))
    except ValueError:
        qty = 1

    if qty < 1:
        cart_item.delete()
        messages.success(request, 'Item removed from cart.')
    elif qty > cart_item.product.stock:
        messages.warning(request, f'Only {cart_item.product.stock} in stock.')
        cart_item.quantity = cart_item.product.stock
        cart_item.save()
    else:
        cart_item.quantity = qty
        cart_item.save()
        messages.success(request, 'Cart updated.')

    return redirect('orders:cart')


# ── Checkout ──────────────────────────────────────────────────────────────────

@buyer_required
def checkout(request):
    cart       = get_or_create_cart(request.user)
    cart_items = cart.cart_items.select_related('product__shop').all()

    if not cart_items.exists():
        messages.warning(request, 'Your cart is empty.')
        return redirect('orders:cart')

    # Group items by shop so buyer can see they may have items from multiple shops
    shops_in_cart = {}
    for item in cart_items:
        shop = item.product.shop
        shops_in_cart.setdefault(shop, []).append(item)

    form = CheckoutForm(request.POST or None)

    if request.method == 'POST' and form.is_valid():
        with transaction.atomic():
            # Create one order per shop
            orders_created = []
            for shop, items in shops_in_cart.items():
                order = Order.objects.create(
                    buyer=request.user,
                    note=form.cleaned_data.get('note', ''),
                    status=Order.Status.PENDING,
                )
                for item in items:
                    OrderItem.objects.create(
                        order=order,
                        product=item.product,
                        quantity=item.quantity,
                        unit_price=item.product.price,
                    )
                    # Deduct stock
                    item.product.stock -= item.quantity
                    item.product.save(update_fields=['stock'])

                order.compute_total()
                orders_created.append(order)

            cart.clear()

        if len(orders_created) == 1:
            messages.success(request, 'Order placed successfully!')
            return redirect('orders:order_detail', pk=orders_created[0].pk)
        else:
            messages.success(request, f'{len(orders_created)} orders placed successfully!')
            return redirect('orders:my_orders')

    context = {
        'cart':           cart,
        'cart_items':     cart_items,
        'shops_in_cart':  shops_in_cart,
        'form':           form,
    }
    return render(request, 'orders/checkout.html', context)


# ── Buyer Order Views ─────────────────────────────────────────────────────────

@buyer_required
def my_orders(request):
    orders = Order.objects.filter(buyer=request.user).prefetch_related('items__product__shop')
    return render(request, 'orders/my_orders.html', {'orders': orders})


@buyer_required
def order_detail(request, pk):
    order = get_object_or_404(Order, pk=pk, buyer=request.user)
    items = order.items.select_related('product__shop').all()
    return render(request, 'orders/order_detail.html', {'order': order, 'items': items})


@buyer_required
def cancel_order(request, pk):
    order = get_object_or_404(Order, pk=pk, buyer=request.user)
    if not order.can_cancel:
        messages.error(request, 'This order can no longer be cancelled.')
        return redirect('orders:order_detail', pk=pk)
    if request.method == 'POST':
        order.status = Order.Status.CANCELLED
        order.save(update_fields=['status'])
        # Restore stock
        for item in order.items.all():
            item.product.stock += item.quantity
            item.product.save(update_fields=['stock'])
        messages.success(request, f'Order #{order.pk} cancelled.')
        return redirect('orders:my_orders')
    return render(request, 'orders/cancel_confirm.html', {'order': order})


# ── Vendor Order Views ────────────────────────────────────────────────────────

@vendor_required
def vendor_orders(request):
    try:
        shop = request.user.shop
    except Exception:
        messages.warning(request, 'Please set up your shop first.')
        return redirect('shops:manage_shop')

    orders = Order.objects.filter(
        items__product__shop=shop
    ).prefetch_related('items__product').select_related('buyer').distinct()

    status_filter = request.GET.get('status', '')
    if status_filter:
        orders = orders.filter(status=status_filter)

    context = {
        'orders':        orders,
        'status_filter': status_filter,
        'status_choices': Order.Status.choices,
    }
    return render(request, 'orders/vendor_orders.html', context)


@vendor_required
def vendor_order_detail(request, pk):
    try:
        shop = request.user.shop
    except Exception:
        return redirect('shops:manage_shop')

    order = get_object_or_404(Order.objects.filter(items__product__shop=shop).distinct(), pk=pk)
    items = order.items.filter(product__shop=shop).select_related('product')

    if request.method == 'POST':
        new_status = request.POST.get('status')
        valid = [Order.Status.CONFIRMED, Order.Status.READY, Order.Status.COMPLETED]
        if new_status in valid:
            order.status = new_status
            order.save(update_fields=['status'])
            messages.success(request, f'Order #{order.pk} marked as {order.get_status_display()}.')
            return redirect('orders:vendor_order_detail', pk=pk)

    context = {'order': order, 'items': items, 'Status': Order.Status}
    return render(request, 'orders/vendor_order_detail.html', context)
