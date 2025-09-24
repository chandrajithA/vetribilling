from django.conf import settings
from django.core.mail import get_connection

def get_email_connection():

    return get_connection(
        backend=settings.EMAIL_BACKEND, 
        host=settings.EMAIL_HOST, 
        port=settings.EMAIL_PORT, 
        username=settings.EMAIL_HOST_USER, 
        password=settings.EMAIL_HOST_PASSWORD, 
        use_tls=settings.EMAIL_USE_TLS, 
        fail_silently=False
    )