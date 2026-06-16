import uuid
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone
from django.conf import settings
from orders.models import Order
from .models import Payment, VendorBankAccount
from .forms import VendorBankAccountForm
from . import paystack as paystack_api


def _has_paystack():
    return bool(getattr(settings, 'PAYSTACK_SECRET_KEY', ''))


# ── Payment Initiation ────────────────────────────────────────────────────────

@login_required
def initiate_payment(request, order_pk):
    order = get_object_or_404(Order, pk=order_pk, buyer=request.user)

    if hasattr(order, 'payment') and order.payment.is_successful:
        messages.info(request, 'This order has already been paid for.')
        return redirect('orders:order_detail', pk=order.pk)

    reference = f"UR-{order.pk}-{uuid.uuid4().hex[:8].upper()}"

    payment, _ = Payment.objects.update_or_create(
        order=order,
        defaults={
            'buyer':     request.user,
            'amount':    order.total_price,
            'reference': reference,
            'status':    Payment.Status.PENDING,
        }
    )

    # Get subaccount code if the order's vendor has one
    subaccount_code = ''
    try:
        # Get the shop from the first order item
        shop = order.items.first().product.shop
        bank_account = shop.vendor.bank_account
        if bank_account.has_subaccount:
            subaccount_code = bank_account.subaccount_code
    except Exception:
        subaccount_code = ''

    context = {
        'order':             order,
        'payment':           payment,
        'paystack_pub_key':  getattr(settings, 'PAYSTACK_PUBLIC_KEY', ''),
        'amount_kobo':       int(order.total_price * 100),
        'email':             request.user.email,
        'reference':         reference,
        'subaccount_code':   subaccount_code,
    }
    return render(request, 'payments/initiate.html', context)


# ── Payment Verification ──────────────────────────────────────────────────────

@login_required
def verify_payment(request, reference):
    payment = get_object_or_404(Payment, reference=reference, buyer=request.user)

    if payment.is_successful:
        messages.info(request, 'Payment already verified.')
        return redirect('orders:order_detail', pk=payment.order.pk)

    if _has_paystack():
        try:
            success = paystack_api.verify_transaction(reference)
            if success:
                payment.status  = Payment.Status.SUCCESS
                payment.paid_at = timezone.now()
                payment.save()
                payment.order.status = 'CONFIRMED'
                payment.order.save(update_fields=['status'])
                messages.success(request, 'Payment successful! Your order is confirmed.')
                return redirect('orders:order_detail', pk=payment.order.pk)
            else:
                payment.status = Payment.Status.FAILED
                payment.save()
                messages.error(request, 'Payment could not be verified. Please try again.')
        except Exception:
            messages.error(request, 'Could not reach payment gateway. Please try again.')
    else:
        # Demo mode
        payment.status  = Payment.Status.SUCCESS
        payment.paid_at = timezone.now()
        payment.save()
        payment.order.status = 'CONFIRMED'
        payment.order.save(update_fields=['status'])
        messages.success(request, 'Demo payment successful! Order confirmed.')
        return redirect('orders:order_detail', pk=payment.order.pk)

    return redirect('payments:initiate', order_pk=payment.order.pk)


# ── Payment History ───────────────────────────────────────────────────────────

@login_required
def payment_history(request):
    payments = Payment.objects.filter(buyer=request.user).select_related('order')
    return render(request, 'payments/history.html', {'payments': payments})


# ── Vendor Bank Account ───────────────────────────────────────────────────────

@login_required
def vendor_bank_account(request):
    """Vendor submits their bank details."""
    if not (request.user.is_vendor and request.user.is_approved_vendor):
        messages.error(request, 'Only approved vendors can access this page.')
        return redirect('shops:home')

    instance = getattr(request.user, 'bank_account', None)
    form     = VendorBankAccountForm(request.POST or None, instance=instance)

    if request.method == 'POST' and form.is_valid():
        bank_account          = form.save(commit=False)
        bank_account.vendor   = request.user
        # Set bank_name from the selected bank_code choice label
        bank_code = form.cleaned_data['bank_code']
        bank_name = dict(form.fields['bank_code'].choices).get(bank_code, bank_code)
        bank_account.bank_name = bank_name
        bank_account.is_verified = False  # Reset until subaccount is created
        bank_account.subaccount_code = ''
        bank_account.save()
        messages.success(
            request,
            'Bank details saved! Your subaccount will be created once an admin processes it.'
        )
        return redirect('payments:vendor_bank_account')

    context = {
        'form':     form,
        'instance': instance,
    }
    return render(request, 'payments/vendor_bank_account.html', context)
