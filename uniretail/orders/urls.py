from django.urls import path
from . import views

app_name = 'orders'

urlpatterns = [
    # Cart
    path('cart/',                          views.cart_view,            name='cart'),
    path('cart/add/<int:product_pk>/',     views.add_to_cart,          name='add_to_cart'),
    path('cart/remove/<int:item_pk>/',     views.remove_from_cart,     name='remove_from_cart'),
    path('cart/update/<int:item_pk>/',     views.update_cart,          name='update_cart'),

    # Checkout & buyer orders
    path('checkout/',                      views.checkout,             name='checkout'),
    path('my-orders/',                     views.my_orders,            name='my_orders'),
    path('my-orders/<int:pk>/',            views.order_detail,         name='order_detail'),
    path('my-orders/<int:pk>/cancel/',     views.cancel_order,         name='cancel_order'),

    # Vendor orders
    path('vendor/orders/',                 views.vendor_orders,        name='vendor_orders'),
    path('vendor/orders/<int:pk>/',        views.vendor_order_detail,  name='vendor_order_detail'),
]
