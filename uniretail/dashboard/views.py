from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Sum
from accounts.models import CustomUser
from shops.models import Shop, Product
from orders.models import Order
from payments.models import Payment, VendorBankAccount


def role_required(role):
    def decorator(view_func):
        from functools import wraps
        @wraps(view_func)
        def wrapper(request, *args, **kwargs):
            if not request.user.is_authenticated:
                return redirect('accounts:login')
            if request.user.role != role and not request.user.is_superuser:
                messages.error(request, 'You do not have permission to access this page.')
                return redirect('shops:home')
            return view_func(request, *args, **kwargs)
        return wrapper
    return decorator


@login_required
def home(request):
    user = request.user
    if user.is_superuser or user.role == CustomUser.Role.ADMIN:
        return redirect('dashboard:admin_dashboard')
    elif user.role == CustomUser.Role.VENDOR:
        return redirect('dashboard:vendor_dashboard')
    else:
        return redirect('shops:home')


# ── Vendor Dashboard ──────────────────────────────────────────────────────────

@login_required
def vendor_dashboard(request):
    if not (request.user.is_vendor and request.user.is_approved_vendor):
        return redirect('shops:home')

    try:
        shop           = request.user.shop
        total_products = shop.products.count()
        total_orders   = Order.objects.filter(items__product__shop=shop).distinct().count()
        pending_orders = Order.objects.filter(
            items__product__shop=shop, status='PENDING'
        ).distinct().count()
        total_revenue  = Payment.objects.filter(
            order__items__product__shop=shop, status='SUCCESS'
        ).distinct().aggregate(total=Sum('amount'))['total'] or 0
    except Exception:
        shop = total_products = total_orders = pending_orders = total_revenue = None

    bank_account = getattr(request.user, 'bank_account', None)

    context = {
        'shop':           shop,
        'total_products': total_products,
        'total_orders':   total_orders,
        'pending_orders': pending_orders,
        'total_revenue':  total_revenue,
        'bank_account':   bank_account,
    }
    return render(request, 'dashboard/vendor.html', context)


# ── Admin Dashboard ───────────────────────────────────────────────────────────

@role_required(CustomUser.Role.ADMIN)
def admin_dashboard(request):
    stats = {
        'total_users':         CustomUser.objects.count(),
        'total_vendors':       CustomUser.objects.filter(role='VENDOR').count(),
        'pending_vendors':     CustomUser.objects.filter(role='VENDOR', is_approved_vendor=False).count(),
        'total_shops':         Shop.objects.count(),
        'total_products':      Product.objects.count(),
        'total_orders':        Order.objects.count(),
        'total_revenue':       Payment.objects.filter(status='SUCCESS').aggregate(
                                   total=Sum('amount'))['total'] or 0,
        'recent_orders':       Order.objects.select_related('buyer').prefetch_related(
                                   'items__product__shop')[:8],
        'pending_vendor_list': CustomUser.objects.filter(role='VENDOR', is_approved_vendor=False),
        'pending_subaccounts': VendorBankAccount.objects.filter(
                                   is_verified=False, subaccount_code=''
                               ).select_related('vendor'),
    }
    return render(request, 'dashboard/admin.html', stats)


@role_required(CustomUser.Role.ADMIN)
def admin_users(request):
    role_filter = request.GET.get('role', '')
    users = CustomUser.objects.all().order_by('-date_joined')
    if role_filter:
        users = users.filter(role=role_filter)
    return render(request, 'dashboard/admin_users.html', {
        'users':       users,
        'role_filter': role_filter,
        'roles':       CustomUser.Role.choices,
    })


@role_required(CustomUser.Role.ADMIN)
def approve_vendor(request, user_pk):
    vendor = get_object_or_404(CustomUser, pk=user_pk, role='VENDOR')
    vendor.is_approved_vendor = True
    vendor.save(update_fields=['is_approved_vendor'])
    messages.success(request, f'{vendor.username} has been approved as a vendor.')
    return redirect('dashboard:admin_dashboard')


@role_required(CustomUser.Role.ADMIN)
def revoke_vendor(request, user_pk):
    vendor = get_object_or_404(CustomUser, pk=user_pk, role='VENDOR')
    vendor.is_approved_vendor = False
    vendor.save(update_fields=['is_approved_vendor'])
    messages.warning(request, f'{vendor.username}\'s vendor access has been revoked.')
    return redirect('dashboard:admin_users')


@role_required(CustomUser.Role.ADMIN)
def create_subaccount(request, bank_account_pk):
    """Admin triggers Paystack subaccount creation for a vendor."""
    bank_account = get_object_or_404(VendorBankAccount, pk=bank_account_pk)

    if bank_account.has_subaccount:
        messages.info(request, f'{bank_account.vendor.username} already has a subaccount.')
        return redirect('dashboard:admin_dashboard')

    from payments.paystack import create_subaccount as paystack_create
    try:
        subaccount_code, subaccount_id = paystack_create(
            business_name=bank_account.vendor.get_full_name() or bank_account.vendor.username,
            bank_code=bank_account.bank_code,
            account_number=bank_account.account_number,
            percentage_charge=100 - float(bank_account.platform_charge_percent),
        )
        bank_account.subaccount_code = subaccount_code
        bank_account.subaccount_id   = subaccount_id
        bank_account.is_verified     = True
        bank_account.save()
        messages.success(
            request,
            f'Subaccount created for {bank_account.vendor.username}: {subaccount_code}'
        )
    except Exception as e:
        messages.error(request, f'Failed to create subaccount: {str(e)}')

    return redirect('dashboard:admin_dashboard')


@role_required(CustomUser.Role.ADMIN)
def admin_orders(request):
    status_filter = request.GET.get('status', '')
    orders = Order.objects.select_related('buyer').prefetch_related(
        'items__product__shop', 'payment'
    ).order_by('-created_at')
    if status_filter:
        orders = orders.filter(status=status_filter)
    return render(request, 'dashboard/admin_orders.html', {
        'orders':         orders,
        'status_filter':  status_filter,
        'status_choices': Order.Status.choices,
    })
