"""
Paystack API helper functions.
All communication with Paystack's REST API lives here.
"""
import requests
from django.conf import settings


PAYSTACK_BASE = 'https://api.paystack.co'


def _headers():
    return {
        'Authorization': f'Bearer {settings.PAYSTACK_SECRET_KEY}',
        'Content-Type':  'application/json',
    }


def create_subaccount(business_name, bank_code, account_number, percentage_charge):
    """
    Create a Paystack subaccount for a vendor.
    Returns (subaccount_code, subaccount_id) on success, or raises Exception.

    Docs: https://paystack.com/docs/api/subaccount/#create
    """
    payload = {
        'business_name':      business_name,
        'bank_code':          bank_code,
        'account_number':     account_number,
        'percentage_charge':  float(percentage_charge),
    }
    resp = requests.post(
        f'{PAYSTACK_BASE}/subaccount',
        json=payload,
        headers=_headers(),
        timeout=15,
    )
    data = resp.json()

    if data.get('status'):
        return (
            data['data']['subaccount_code'],  # e.g. ACCT_xxxxxxxxxx
            str(data['data']['id']),
        )
    raise Exception(data.get('message', 'Failed to create Paystack subaccount'))


def verify_transaction(reference):
    """
    Verify a Paystack transaction by reference.
    Returns True if payment was successful, False otherwise.

    Docs: https://paystack.com/docs/api/transaction/#verify
    """
    resp = requests.get(
        f'{PAYSTACK_BASE}/transaction/verify/{reference}',
        headers=_headers(),
        timeout=10,
    )
    data = resp.json()
    return (
        data.get('status') and
        data.get('data', {}).get('status') == 'success'
    )


def resolve_account(account_number, bank_code):
    """
    Resolve a bank account number to get the account name.
    Useful for confirming the vendor's account details before saving.

    Docs: https://paystack.com/docs/api/verification/#resolve-account
    """
    resp = requests.get(
        f'{PAYSTACK_BASE}/bank/resolve',
        params={'account_number': account_number, 'bank_code': bank_code},
        headers=_headers(),
        timeout=10,
    )
    data = resp.json()
    if data.get('status'):
        return data['data'].get('account_name', '')
    return None
