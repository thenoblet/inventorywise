from celery import shared_task
from django.core.mail import EmailMessage, BadHeaderError
from django.db.models import F
from django.conf import settings
from smtplib import SMTPException
from .models import Product
from .utils import generate_pdf_report, get_report_recipients
import logging

logger = logging.getLogger(__name__)

@shared_task(
    bind=True,
    max_retries=3,
    default_retry_delay=300,  # 5 minutes
    autoretry_for=(Exception,),
    retry_backoff=True
)
def send_stock_report(self):
    """
    Task to generate and email a PDF report for products that are at or below
    their minimum stock threshold.
    
    Features:
    - Monitors only products with stock levels at or below minimum threshold
    - Automatic retry on failure with exponential backoff
    - Comprehensive logging
    - Configurable email settings
    - Detailed error handling
    
    Returns:
        str: Status message indicating whether report was sent or no low stock found
    """
    try:
        
        recipients = get_report_recipients()
        if not recipients:
            logger.error("No valid recipients found for stock report")
            return "No valid recipients found for stock report"
        
        # Fetch only products at or below minimum threshold
        low_stock_products = Product.objects.filter(
            stock_quantity__lte=F('min_stock_threshold')
        ).values(
            'name',
            'stock_quantity',
            'min_stock_threshold',
            'max_stock_threshold'
        )

        # Prepare report data
        report_data = [{
            'name': product['name'],
            'current_stock': product['stock_quantity'],
            'min_threshold': product['min_stock_threshold'],
            'max_threshold': product['max_stock_threshold']
        } for product in low_stock_products]

        if not report_data:
            logger.info("No products found below minimum stock threshold")
            return "No low stock products to report."

        # Log which products are low on stock
        logger.warning(
            "Low stock detected for products: %s",
            ", ".join(item['name'] for item in report_data)
        )

        # Generate PDF report
        try:
            pdf = generate_pdf_report(report_data)
            if not pdf:
                raise ValueError("PDF generation returned empty result")
        except Exception as e:
            logger.error(f"Failed to generate PDF report: {str(e)}")
            raise

        # Get email settings from Django settings with fallbacks
        # admin_email = getattr(settings, 'STOCK_ALERT_EMAIL', 'admin@yourstore.com')
        from_email = getattr(settings, 'COMPANY_EMAIL', 'myinventorywise@gmail.com')

        # Create email with summary in body
        email_body = (
            "Low Stock Alert Report\n\n"
            "The following products are at or below their minimum stock threshold:\n\n"
        )
        for item in report_data:
            email_body += (
                f"- {item['name']}: {item['current_stock']} units "
                f"(Minimum: {item['min_threshold']})\n"
            )
        email_body += (
            "\nPlease find attached the detailed report."
            "Note: This report has been sent to all Admins and Stock  Managers"           
        )

        # Send the email
        try:
            email = EmailMessage(
                subject=f"Low Stock Alert - {len(report_data)} Products Need Attention",
                body=email_body,
                from_email=from_email,
                to=['mrnobletlearns@gmail.com'],
                bcc=recipients
            )
            email.attach('low_stock_report.pdf', pdf, 'application/pdf')
            email.send(fail_silently=False)
            
            logger.info(
                f"Low stock report sent to {len(recipients)} recipients "
                f"for {len(report_data)} products"
            )
        except BadHeaderError as e:
            # This exception indicates a misconfiguration, like a bad email header
            logger.error(f"Failed to send email due to bad header: {str(e)}")
            raise self.retry(exc=e, countdown=60)  # Retry in 1 minute
        except SMTPException as e:
            # Catch general SMTP errors
            if "Invalid recipient" in str(e):  # Handle invalid email case
                logger.error(f"Invalid recipient address: {str(e)}")
                return "Invalid email address, task not retried."
            else:
                logger.warning(f"SMTP error occurred, retrying...: {str(e)}")
                raise self.retry(exc=e)  # Retry the task
        except Exception as e:
            # Any other general exception
            logger.error(f"Unexpected error: {str(e)}")
            raise self.retry(exc=e)

        logger.info(f"Low stock report sent for {len(report_data)} products")
        logger.info(f"Low stock report sent successfully to {len(recipients)} recipients.")
        return f"Low stock report sent for {len(report_data)} products!"

    except Exception as e:
        logger.error(f"Failed to process low stock report: {str(e)}")
        raise
    