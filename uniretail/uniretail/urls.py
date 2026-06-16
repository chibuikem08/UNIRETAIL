from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.shortcuts import redirect

handler404 = 'uniretail.views.handler404'
handler500 = 'uniretail.views.handler500'

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', lambda request: redirect('shops:home'), name='root'),
    path('accounts/', include('accounts.urls', namespace='accounts')),
    path('shops/',    include('shops.urls',    namespace='shops')),
    path('orders/',   include('orders.urls',   namespace='orders')),
    path('payments/', include('payments.urls', namespace='payments')),
    path('dashboard/', include('dashboard.urls', namespace='dashboard')),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
