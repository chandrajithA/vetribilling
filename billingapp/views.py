from django.shortcuts import render, redirect, get_object_or_404
from .forms import InvoiceForm
from .models import Invoice, InvoiceItem
from django.db import transaction
from django.contrib.auth.decorators import login_required
from django.contrib.auth import logout
from django.views.decorators.cache import never_cache
from django.views.decorators.http import require_POST
from django.conf import settings


@login_required
def dashboard(request):
    invoices = Invoice.objects.all().order_by("-created_at")
    grand_total = sum(inv.total_amount for inv in invoices)
    return render(request, "dashboard.html", {"invoices": invoices,"grand_total":grand_total})


@login_required
@never_cache
def create_invoice(request):
    if request.method == "POST":
        form = InvoiceForm(request.POST)
        if form.is_valid():
            with transaction.atomic():
                invoice = form.save()

                # Save product items
                product_names = request.POST.getlist("product_name[]")
                unit_prices = request.POST.getlist("unit_price[]")
                quantities = request.POST.getlist("quantity[]")
                tax_percentages = request.POST.getlist("tax_percentage[]")

                for i in range(len(product_names)):
                    if product_names[i].strip() == "":
                        continue
                    InvoiceItem.objects.create(
                        invoice=invoice,
                        product_name=product_names[i],
                        unit_price=unit_prices[i],
                        quantity=quantities[i],
                        tax_percentage=tax_percentages[i],
                    )
            return redirect("invoice_detail", invoice.id)
    else:
        form = InvoiceForm()
    return render(request, "create_invoice.html", {"form": form})




@login_required
def invoice_detail(request, pk):
    invoice = Invoice.objects.filter(pk=pk).first()
    return render(request, "invoice_detail.html", {"invoice": invoice})



@login_required
@never_cache
def edit_invoice(request, pk):
    invoice = Invoice.objects.filter(pk=pk).first()

    if request.method == "POST":
        form = InvoiceForm(request.POST, instance=invoice)

        if form.is_valid():
            invoice = form.save(commit=False)
            invoice.save()

            # Delete old items and re-create
            invoice.items.all().delete()

            product_names = request.POST.getlist("product_name[]")
            unit_prices = request.POST.getlist("unit_price[]")
            quantities = request.POST.getlist("quantity[]")
            taxes = request.POST.getlist("tax_percentage[]")

            for i in range(len(product_names)):
                if product_names[i].strip():
                    InvoiceItem.objects.create(
                        invoice=invoice,
                        product_name=product_names[i],
                        unit_price=float(unit_prices[i]),
                        quantity=int(quantities[i]),
                        tax_percentage=float(taxes[i]) if taxes[i] else 0,
                    )

            return redirect("invoice_detail", pk=invoice.pk)

    else:
        form = InvoiceForm(instance=invoice)

    return render(request, "edit_invoice.html", {
        "form": form,
        "invoice": invoice,
    })





@login_required
def delete_invoice(request, pk):
    invoice = Invoice.objects.filter(pk=pk).first()
    invoice.delete()
    return redirect("dashboard")




@login_required
def user_logout(request):
    logout(request)
    return redirect('login')


# from django.core.mail import EmailMessage
# from .email_utils import get_email_connection
# from django.http import JsonResponse
# from django.views.decorators.csrf import csrf_exempt

# @login_required
# @require_POST
# def send_pdf_email(request,invoice_id):
#     try:

#         invoice = Invoice.objects.filter(id=invoice_id).first()
#         if not invoice:
#             return JsonResponse({"status": "error", "message": "Invoice not found"}, status=404)
        
#         pdf_file = request.FILES.get("pdf_file")
#         if not pdf_file:
#             return JsonResponse({"status": "error", "message": "No file uploaded"}, status=400)
        
#         recipient_email = invoice.customer_email
#         if not recipient_email:
#             return JsonResponse({"status": "error", "message": "User has no email"}, status=400)
        
#         connection = get_email_connection()
#         if not connection:
#             return {"status": "error"}

#         email = EmailMessage(
#             subject=f"Invoice - #{invoice.id} - Vetri Shoppings",
#             body=f"""Hello {invoice.customer_name} ,

# Thank you for shopping with us!

# Your invoice number is #{invoice.id}.
# Please find your attached invoice as a PDF.

# Best regards,  
# Vetri Shoppings
# """,
#             from_email=settings.DEFAULT_FROM_EMAIL,
#             to=[recipient_email],
#             connection=connection
#         )

#         email.attach(pdf_file.name, pdf_file.read(), "application/pdf") 
#         email.send()
        

#         return JsonResponse({"status": "success", "message": "Email is being sent in the background"})
#     except Exception as e:
#         import traceback
#         print("EMAIL ERROR:", traceback.format_exc())
#         return JsonResponse({"status": "error", "message": str(e)}, status=500)

import os
import base64
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail, Attachment, FileContent, FileName, FileType, Disposition
from .models import Invoice  # adjust import if needed


@login_required
@require_POST
def send_pdf_email(request, invoice_id):
    try:
        # Fetch invoice
        invoice = Invoice.objects.filter(id=invoice_id).first()
        if not invoice:
            return JsonResponse({"status": "error", "message": "Invoice not found"}, status=404)

        # Get uploaded PDF
        pdf_file = request.FILES.get("pdf_file")
        if not pdf_file:
            return JsonResponse({"status": "error", "message": "No file uploaded"}, status=400)

        # Get recipient
        recipient_email = invoice.email
        if not recipient_email:
            return JsonResponse({"status": "error", "message": "User has no email"}, status=400)

        # Create email
        message = Mail(
            from_email=os.environ.get("DEFAULT_FROM_EMAIL"),
            to_emails=recipient_email,
            subject=f"Invoice - #{invoice.invoice_number} - Vetri IT Systems",
            plain_text_content=f"""Hello {invoice.name},

Thank you for choosing our service!

Your invoice number is #{invoice.invoice_number}.
Please find your attached invoice as a PDF.

Best regards,
Vetri IT Systems
"""
        )

        # Attach PDF (must be base64 for SendGrid)
        file_data = pdf_file.read()
        encoded_file = base64.b64encode(file_data).decode()

        attachment = Attachment(
            FileContent(encoded_file),
            FileName(pdf_file.name),
            FileType("application/pdf"),
            Disposition("attachment"),
        )
        message.attachment = attachment

        # Send with SendGrid API
        sg = SendGridAPIClient(os.environ.get("SENDGRID_API_KEY"))
        response = sg.send(message)

        return JsonResponse({
            "status": "success",
            "message": f"Email sent (SendGrid status {response.status_code})"
        })

    except Exception as e:
        import traceback
        print("EMAIL ERROR:", traceback.format_exc())
        return JsonResponse({"status": "error", "message": str(e)}, status=500)