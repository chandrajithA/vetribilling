from django.urls import path
from . import views
from django.contrib.auth import views as auth_views
from django.http import HttpResponse

urlpatterns = [
    path("", views.dashboard, name="dashboard"),
    
    path('login/', auth_views.LoginView.as_view(template_name='login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(next_page='login'), name='logout'),

    path("create-invoice/", views.create_invoice, name="create_invoice"),
    path("invoice/<int:pk>/", views.invoice_detail, name="invoice_detail"),

    path("invoice/<int:pk>/edit/", views.edit_invoice, name="edit_invoice"),
    path("invoice/<int:pk>/delete/", views.delete_invoice, name="delete_invoice"),  
    path("invoice/send-pdf-email/<int:invoice_id>/", views.send_pdf_email, name="send_pdf_email"),
    path('.well-known/appspecific/com.chrome.devtools.json', lambda request: HttpResponse('{}', content_type='application/json')),
]
