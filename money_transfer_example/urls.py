from django.contrib import admin
from django.urls import path, include

from transferapp.views import TransferPage, TransferSuccessPage

urlpatterns = [
    path('', TransferPage.as_view(), name='transfer_page'),
    path('transfer/success/<int:src_user>/', TransferSuccessPage.as_view(),
         name='transfer_success_page'),

    path('api/', include('api.urls', namespace='api')),

    path('admin/', admin.site.urls),
]
