from django.urls import path
from . import views

app_name = 'shops'

urlpatterns = [
    # Public
    path('',         views.home,   name='home'),
    path('search/',  views.search, name='search'),

    # Vendor management (must come BEFORE slug patterns)
    path('vendor/shop/',                     views.manage_shop,    name='manage_shop'),
    path('vendor/products/',                 views.product_list,   name='product_list'),
    path('vendor/products/add/',             views.product_create, name='product_create'),
    path('vendor/products/<int:pk>/edit/',   views.product_edit,   name='product_edit'),
    path('vendor/products/<int:pk>/delete/', views.product_delete, name='product_delete'),

    # Public slug patterns (must come AFTER vendor routes)
    path('<slug:slug>/',                  views.shop_detail,    name='shop_detail'),
    path('<slug:shop_slug>/<slug:slug>/', views.product_detail, name='product_detail'),
]
