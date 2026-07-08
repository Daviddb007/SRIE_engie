"""Services package — business logic layer."""
from core.services.admin_auth_service import AdminAuthService
from core.services.admin_service import AdminService
from core.services.client_service import ClientService
from core.services.project_service import ProjectService
from core.services.quotation_service import QuotationService
from core.services.catalog_service import CatalogService
from core.services.cotizador_validation_service import CotizadorValidationService


def generate_quotation_pdf(quotation):
    from core.services.pdf_service import generate_quotation_pdf as _gen
    return _gen(quotation)


def generate_intelligence_report_pdf(company_name, contact_name, diagnosis, generated_at=None):
    from core.services.pdf_service import generate_intelligence_report_pdf as _gen
    return _gen(company_name, contact_name, diagnosis, generated_at)


def send_telegram_async(message, app):
    from core.services.notification_service import send_telegram_async as _send
    return _send(message, app)


def send_contact_email_async(data, app):
    from core.services.notification_service import send_contact_email_async as _send
    return _send(data, app)


__all__ = [
    'AdminAuthService',
    'AdminService',
    'ClientService',
    'ProjectService',
    'QuotationService',
    'CatalogService',
    'CotizadorValidationService',
    'generate_quotation_pdf',
    'generate_intelligence_report_pdf',
    'send_telegram_async',
    'send_contact_email_async',
]
