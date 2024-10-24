from django.utils.text import slugify
from django.utils import timezone
from django.conf import settings
from django.template.loader import render_to_string
from xhtml2pdf import pisa
from io import BytesIO
import logging
import os
from datetime import datetime

from user_management.models import User

logger = logging.getLogger(__name__)

def generate_sku(name, category):
    """
    Generates a SKU based on the product name and category.

    The SKU is composed of:
    - The first 3 characters of the product's name (slugified),
    - The first 4 characters of the category name in uppercase,
    - The current date (in YYYY-MM-DD format) to ensure uniqueness.
    """
    base_sku = slugify(name[:4]).upper()
    category_initial = category.name[:4].upper()
    current_date = timezone.now().strftime('%Y-%m-%d')

    return f"{category_initial}-{base_sku}-{current_date}"


def get_report_recipients():
    """
    Get all users who should receive the stock report:
    - Superusers
    - Staff users in the 'Stock Managers' group
    
    Returns:
        list: List of email addresses
    """
    recipients = set()  # Using set to avoid duplicate emails

    try:
        # Get all superusers
        superusers = User.objects.filter(userrole__role__name__in=['admin', 'stock_manager']).distinct()
        recipients.update(superusers)

        # Remove any empty emails
        recipients.discard('')
        recipients.discard(None)

        if not recipients:
            logger.warning("No recipients found for stock report")
            
        return list(recipients)

    except Exception as e:
        logger.error(f"Error getting report recipients: {str(e)}")
        raise


def get_static_file_path(filename):
    """Helper function to get the absolute path of static files."""
    return os.path.join(settings.STATIC_ROOT, filename)


def prepare_report_data(report_data):
    """
    Prepares and enriches the report data with additional calculations
    
    Args:
        report_data (list): Raw report data
        
    Returns:
        tuple: Enriched report data and context dictionary
    """
    if not isinstance(report_data, list):
        raise ValueError("report_data must be a list")
        
    # Add input validation
    required_fields = {'name', 'current_stock', 'min_threshold'}
    for item in report_data:
        missing_fields = required_fields - set(item.keys())
        if missing_fields:
            raise ValueError(f"Missing required fields: {missing_fields}")
    
    for item in report_data:
        if item['min_threshold'] > 0:
            item['stock_level_pct'] = (item['current_stock'] / item['min_threshold']) * 100
        else:
            item['stock_level_pct'] = 100.0
            
    # Sort data with low stock items first
    sorted_data = sorted(
        report_data,
        key=lambda x: (x['current_stock'] <= x['min_threshold'], x['name']),
        reverse=True
    )
    
    low_stock_items = [
        item for item in sorted_data 
        if item['current_stock'] <= item['min_threshold']
    ]
    
    critical_items = [
        item for item in low_stock_items 
        if item['current_stock'] == 0
    ]
    
    total_value = sum(
        item.get('current_stock', 0) * item.get('unit_price', 0) 
        for item in sorted_data
    )
    
    avg_stock_level = (
        sum(item['stock_level_pct'] for item in sorted_data) / len(sorted_data)
        if sorted_data else 0
    )
    
    # Count items below 50% stock
    items_below_50 = sum(1 for item in sorted_data if item['stock_level_pct'] < 50)
    
    context = {
        'report': sorted_data,
        'generated_at': datetime.now(),
        'company_name': getattr(settings, 'COMPANY_NAME', 'InventoryWise'),
        'total_products': len(report_data),
        'low_stock_count': len(low_stock_items),
        'low_stock_items': low_stock_items,
        'critical_items_count': len(critical_items),
        'critical_items': critical_items,
        'total_inventory_value': total_value,
        'report_type': 'Low Stock Alert' if low_stock_items else 'Stock Report',
        'report_summary': {
            'avg_stock_level': avg_stock_level,
            'items_below_50_pct': items_below_50
        }
    }
    
    return sorted_data, context

def generate_pdf_report(report_data, template_name='emails/stock_report_template.html'):
    """
    Generates a PDF report from stock data with proper styling and formatting.
    
    Args:
        report_data (list): List of dictionaries containing stock information
        template_name (str): Name of the HTML template to use
        
    Returns:
        bytes: PDF file content as bytes if successful, None if failed
    """
    try:
        # Prepare and enrich report data
        _, context = prepare_report_data(report_data)
        
        # Ensure low_stock_items is a list
        if not isinstance(context.get('low_stock_items'), list):
            context['low_stock_items'] = []

        html = render_to_string(template_name, context)
        
        if not html:
            raise ValueError("Rendered HTML is empty.")
        print(f"Rendered HTML Length: {len(html)}")
        
        styled_html = f"""
            <!DOCTYPE html>
            <html>
                <head>
                    <meta charset="UTF-8">
                    <style>
                        body {{
                            font-family: Arial, sans-serif;
                            font-size: 12pt;
                            color: #333;
                            line-height: 1.5;
                        }}
                        
                        h1, h2, h3, h4 {{
                            color: #2c3e50;
                            margin-bottom: 10pt;
                        }}
                        
                        h1 {{ font-size: 24pt; }}
                        h2 {{ font-size: 20pt; }}
                        h3 {{ font-size: 18pt; }}
                        h4 {{ font-size: 16pt; }}

                        .table {{
                            width: 100%;
                            border-collapse: collapse;
                            margin: 8pt 0;
                        }}

                        .table th {{
                            background-color: #2c3e50;
                            color: white;
                            padding: 6pt;
                            text-align: left;
                            border: 1px solid #bdc3c7;
                        }}

                        .table td {{
                            padding: 4pt 6pt;
                            border: 1px solid #bdc3c7;
                        }}

                        .alert-section {{
                            background-color: #fff3cd;
                            padding: 10pt;
                            margin: 15pt 0;
                        }}

                        .warning-row {{
                            background-color: #fff3cd;
                        }}

                        .numeric {{
                            font-family: Courier;
                            text-align: right;
                        }}

                        .status-critical {{ color: #c0392b; font-weight: bold; }}
                        .status-warning {{ color: #e67e22; font-weight: bold; }}
                        .status-normal {{ color: #27ae60; }}

                        ul {{
                            margin: 5pt 0;
                            padding-left: 15pt;
                        }}

                        li {{
                            margin-bottom: 3pt;
                        }}

                        .footer {{
                            text-align: center;
                            font-size: 9pt;
                            color: #7f8c8d;
                            padding-top: 5pt;
                            border-top: 1pt solid #bdc3c7;
                        }}
                    </style>
                </head>
                <body>
                {html}
                    <div class="footer">
                        Generated by {context['company_name']} on {context['generated_at'].strftime('%Y-%m-%d %H:%M:%S')}
                    </div>
                </body>
            </html>
        """

        result = BytesIO()
        pdf = pisa.pisaDocument(
            BytesIO(styled_html.encode("UTF-8")),
            result,
            encoding='UTF-8',
            show_error_as_pdf=True
        )

        if pdf.err:
            logger.error(f"Error generating PDF: {pdf.err}")
            return None

        logger.info(
            f"Successfully generated PDF report with {len(report_data)} items, "
            f"including {context['low_stock_count']} low stock items"
        )
        return result.getvalue()

    except Exception as e:
        logger.error(f"Failed to generate PDF report: {str(e)}", exc_info=True)
        return None
