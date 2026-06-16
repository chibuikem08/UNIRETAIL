from django import forms
from .models import VendorBankAccount

# Nigerian banks supported by Paystack with their bank codes
NIGERIAN_BANKS = [
    ('', '-- Select Your Bank --'),
    ('044', 'Access Bank'),
    ('063', 'Access Bank (Diamond)'),
    ('035A', 'ALAT by WEMA'),
    ('401', 'ASO Savings and Loans'),
    ('023', 'Citibank Nigeria'),
    ('050', 'EcoBank Nigeria'),
    ('562', 'Ekondo Microfinance Bank'),
    ('070', 'Fidelity Bank'),
    ('011', 'First Bank of Nigeria'),
    ('214', 'First City Monument Bank (FCMB)'),
    ('058', 'Guaranty Trust Bank (GTB)'),
    ('030', 'Heritage Bank'),
    ('301', 'Jaiz Bank'),
    ('082', 'Keystone Bank'),
    ('526', 'Parallex Bank'),
    ('076', 'Polaris Bank'),
    ('101', 'Providus Bank'),
    ('221', 'Stanbic IBTC Bank'),
    ('068', 'Standard Chartered Bank'),
    ('232', 'Sterling Bank'),
    ('100', 'Suntrust Bank'),
    ('032', 'Union Bank of Nigeria'),
    ('033', 'United Bank for Africa (UBA)'),
    ('215', 'Unity Bank'),
    ('035', 'WEMA Bank'),
    ('057', 'Zenith Bank'),
]


class VendorBankAccountForm(forms.ModelForm):
    bank_code = forms.ChoiceField(
        choices=NIGERIAN_BANKS,
        label='Bank Name'
    )

    class Meta:
        model  = VendorBankAccount
        fields = ['bank_code', 'account_number', 'account_name', 'bvn']
        labels = {
            'account_number': 'Account Number',
            'account_name':   'Account Name (as on bank record)',
            'bvn':            'BVN (optional but recommended)',
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for name, field in self.fields.items():
            field.widget.attrs.update({'class': 'form-control'})
        self.fields['account_number'].widget.attrs.update({'maxlength': '10', 'placeholder': '0123456789'})
        self.fields['bvn'].widget.attrs.update({'maxlength': '11', 'placeholder': '12345678901'})
        self.fields['bvn'].required = False

    def clean_account_number(self):
        acct = self.cleaned_data.get('account_number', '')
        if not acct.isdigit():
            raise forms.ValidationError('Account number must contain digits only.')
        if len(acct) != 10:
            raise forms.ValidationError('Account number must be exactly 10 digits.')
        return acct
