from django.urls import path
from . import views

app_name = 'dashboard'

urlpatterns = [
    path('',                                        views.home,             name='home'),
    path('vendor/',                                 views.vendor_dashboard, name='vendor_dashboard'),
    path('admin/',                                  views.admin_dashboard,  name='admin_dashboard'),
    path('admin/users/',                            views.admin_users,      name='admin_users'),
    path('admin/users/<int:user_pk>/approve/',      views.approve_vendor,   name='approve_vendor'),
    path('admin/users/<int:user_pk>/revoke/',       views.revoke_vendor,    name='revoke_vendor'),
    path('admin/subaccount/<int:bank_account_pk>/', views.create_subaccount, name='create_subaccount'),
    path('admin/orders/',                           views.admin_orders,     name='admin_orders'),
]
