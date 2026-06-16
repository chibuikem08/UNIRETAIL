from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Q
from .models import Shop, Product, ShopCategory
from .forms import ShopForm, ProductForm


# ── Public Views ─────────────────────────────────────────────────────────────

def home(request):
    """Marketplace landing — list all open shops with optional search/filter."""
    shops = Shop.objects.filter(is_open=True).select_related('vendor')

    query    = request.GET.get('q', '')
    category = request.GET.get('category', '')

    if query:
        shops = shops.filter(
            Q(name__icontains=query) | Q(description__icontains=query)
        )
    if category:
        shops = shops.filter(category=category)

    context = {
        'shops':      shops,
        'query':      query,
        'category':   category,
        'categories': ShopCategory.choices,
    }
    return render(request, 'shops/home.html', context)


def shop_detail(request, slug):
    """Show a shop and all its available products."""
    shop     = get_object_or_404(Shop, slug=slug, is_open=True)
    products = shop.products.filter(is_available=True)

    query    = request.GET.get('q', '')
    category = request.GET.get('category', '')

    if query:
        products = products.filter(
            Q(name__icontains=query) | Q(description__icontains=query)
        )
    if category:
        products = products.filter(category=category)

    from .models import ProductCategory
    context = {
        'shop':       shop,
        'products':   products,
        'query':      query,
        'category':   category,
        'categories': ProductCategory.choices,
    }
    return render(request, 'shops/shop_detail.html', context)


def product_detail(request, shop_slug, slug):
    """Show a single product."""
    shop    = get_object_or_404(Shop, slug=shop_slug)
    product = get_object_or_404(Product, shop=shop, slug=slug, is_available=True)
    return render(request, 'shops/product_detail.html', {'shop': shop, 'product': product})


# ── Vendor Views ─────────────────────────────────────────────────────────────

def vendor_required(view_func):
    """Decorator: user must be an approved vendor."""
    from functools import wraps
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect('accounts:login')
        if not request.user.is_vendor:
            messages.error(request, 'Only vendors can access this page.')
            return redirect('shops:home')
        if not request.user.is_approved_vendor:
            messages.warning(request, 'Your vendor account is pending admin approval.')
            return redirect('shops:home')
        return view_func(request, *args, **kwargs)
    return wrapper


@vendor_required
def manage_shop(request):
    """Vendor creates or edits their shop."""
    shop = getattr(request.user, 'shop', None)
    form = ShopForm(request.POST or None, request.FILES or None, instance=shop)

    if request.method == 'POST' and form.is_valid():
        new_shop        = form.save(commit=False)
        new_shop.vendor = request.user
        new_shop.save()
        messages.success(request, 'Shop saved successfully!')
        return redirect('shops:manage_shop')

    context = {'form': form, 'shop': shop}
    return render(request, 'shops/manage_shop.html', context)


@vendor_required
def product_list(request):
    """Vendor sees all their products."""
    try:
        shop     = request.user.shop
        products = shop.products.all()
    except Shop.DoesNotExist:
        messages.warning(request, 'Please create your shop first.')
        return redirect('shops:manage_shop')

    return render(request, 'shops/product_list.html', {'shop': shop, 'products': products})


@vendor_required
def product_create(request):
    """Vendor adds a new product."""
    try:
        shop = request.user.shop
    except Shop.DoesNotExist:
        messages.warning(request, 'Please create your shop first.')
        return redirect('shops:manage_shop')

    form = ProductForm(request.POST or None, request.FILES or None)
    if request.method == 'POST' and form.is_valid():
        product      = form.save(commit=False)
        product.shop = shop
        product.save()
        messages.success(request, f'"{product.name}" added successfully!')
        return redirect('shops:product_list')

    return render(request, 'shops/product_form.html', {'form': form, 'action': 'Add'})


@vendor_required
def product_edit(request, pk):
    """Vendor edits one of their products."""
    try:
        shop = request.user.shop
    except Shop.DoesNotExist:
        return redirect('shops:manage_shop')

    product = get_object_or_404(Product, pk=pk, shop=shop)
    form    = ProductForm(request.POST or None, request.FILES or None, instance=product)

    if request.method == 'POST' and form.is_valid():
        form.save()
        messages.success(request, f'"{product.name}" updated!')
        return redirect('shops:product_list')

    return render(request, 'shops/product_form.html', {'form': form, 'action': 'Edit', 'product': product})


@vendor_required
def product_delete(request, pk):
    """Vendor deletes one of their products."""
    try:
        shop = request.user.shop
    except Shop.DoesNotExist:
        return redirect('shops:manage_shop')

    product = get_object_or_404(Product, pk=pk, shop=shop)
    if request.method == 'POST':
        name = product.name
        product.delete()
        messages.success(request, f'"{name}" deleted.')
        return redirect('shops:product_list')

    return render(request, 'shops/product_confirm_delete.html', {'product': product})


def search(request):
    """Global search across shops and products."""
    query    = request.GET.get('q', '').strip()
    shops    = []
    products = []

    if query:
        from django.db.models import Q
        shops = Shop.objects.filter(
            is_open=True
        ).filter(
            Q(name__icontains=query) | Q(description__icontains=query)
        )
        products = Product.objects.filter(
            is_available=True, shop__is_open=True
        ).filter(
            Q(name__icontains=query) | Q(description__icontains=query)
        ).select_related('shop')

    return render(request, 'shops/search.html', {
        'query':    query,
        'shops':    shops,
        'products': products,
    })
