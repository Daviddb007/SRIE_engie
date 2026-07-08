"""Admin service — business logic layer."""
import re
from typing import Any, Dict, List
from decimal import Decimal
from datetime import datetime

from core.services.admin_auth_service import AdminAuthService
from core.errors import ValidationError, ConflictError, NotFoundError
from core.models.admin_user import AdminUser
from core.models.client import Client
from core.models.project import Project
from core.models.quotation import Quotation
from core.models.capability import Capability
from core.models.automation import Automation
from core.models.service import Service


class AdminService:
    """Centralized service layer for admin operations across domains."""

    @staticmethod
    def handle_calendar_request(request_data: Dict) -> Dict[str, Any]:
        """Handle calendar requests with validation and parsing.
        
        Args:
            request_data: Raw request data
            
        Returns:
            Parsed and validated calendar data
            
        Raises:
            ValidationError: If data is invalid
        """
        if not request_data or not isinstance(request_data, dict):
            raise ValidationError('Invalid calendar request data')

        # Parse and validate start_date
        start_date = request_data.get('start')
        if not start_date:
            raise ValidationError('start date is required')
        try:
            start_date = datetime.fromisoformat(start_date.replace('Z', '+00:00'))
        except ValueError:
            raise ValidationError('Invalid start date format')

        # Parse and validate end_date
        end_date = request_data.get('end')
        if not end_date:
            raise ValidationError('end date is required')
        try:
            end_date = datetime.fromisoformat(end_date.replace('Z', '+00:00'))
        except ValueError:
            raise ValidationError('Invalid end date format')

        # Validate date range
        if start_date >= end_date:
            raise ValidationError('start date must be before end date')

        # Parse and validate events if present
        events = request_data.get('events', [])
        if events and not isinstance(events, list):
            raise ValidationError('events must be a list')

        return {
            'start': start_date,
            'end': end_date,
            'events': events,
        }

    @staticmethod
    def get_dashboard_stats() -> Dict[str, Any]:
        """Get dashboard statistics for admin panel.
        
        Returns:
            Dictionary with all dashboard statistics
        """
        clients = Client.query.count()
        projects = Project.query.count()
        active_projects = Project.query.filter_by(status='active').count()
        quotations = Quotation.query.count()
        pending_quotations = Quotation.query.filter_by(status='draft').count()
        capabilities = Capability.query.count()
        automations = Automation.query.count()
        services = Service.query.count()

        return {
            'clients': clients,
            'projects': projects,
            'active_projects': active_projects,
            'quotations': quotations,
            'pending_quotations': pending_quotations,
            'capabilities': capabilities,
            'automations': automations,
            'services': services,
        }

    @staticmethod
    def validate_and_parse_calculation_data(request_data: Dict) -> Dict[str, Any]:
        """Validate and parse quotation calculation data.
        
        Args:
            request_data: Raw request data with items and discount
            
        Returns:
            Parsed calculation data
            
        Raises:
            ValidationError: If data is invalid
        """
        if not request_data:
            raise ValidationError('Request data is required')

        items = request_data.get('items', [])
        if not items or not isinstance(items, list):
            raise ValidationError('items is required and must be a list')

        discount_pct = request_data.get('discount_pct', 0)
        try:
            discount_pct = float(discount_pct)
            if discount_pct < 0 or discount_pct > 100:
                raise ValueError()
        except (ValueError, TypeError):
            raise ValidationError('discount_pct must be a number between 0 and 100')

        return {'items': items, 'discount_pct': discount_pct}

    @staticmethod
    def generate_quotation_number() -> str:
        """Generate a unique quotation number.
        
        Returns:
            Unique quotation number
        """
        today = datetime.now()
        month_year = today.strftime('%y%m')

        last_quotation = Quotation.query.filter(
            Quotation.quotation_number.like(f'%{month_year}%')
        ).order_by(Quotation.quotation_number.desc()).first()

        if not last_quotation:
            return f'QT-{month_year}-0001'

        try:
            last_number = int(last_quotation.quotation_number.split('-')[2])
            new_number = last_number + 1
            return f'QT-{month_year}-{new_number:04d}'
        except (IndexError, ValueError):
            return f'QT-{month_year}-0001'

    @staticmethod
    def validate_form_data(fields: List[str], form_data: Dict[str, Any]) -> List[str]:
        """Validate form data for required fields.
        
        Args:
            fields: List of required field names
            form_data: Form data dictionary
            
        Returns:
            List of error messages (empty if valid)
        """
        errors = []
        for field in fields:
            value = form_data.get(field)
            if not value:
                errors.append(f'{field} es requerido')
        return errors

    @staticmethod
    def sanitize_string(value: str) -> str:
        """Sanitize string input for safe use.
        
        Args:
            value: String to sanitize
            
        Returns:
            Sanitized string
        """
        if not isinstance(value, str):
            return ''

        value = value.strip()
        value = re.sub(r'[<>&"\'\n\r\t]', '', value)

        return value

    @staticmethod
    def get_paginated_data(query, page: int, per_page: int):
        """Get paginated results from a query.
        
        Args:
            query: SQLAlchemy query object
            page: Page number (1-based)
            per_page: Items per page
            
        Returns:
            Tuple of (items, total_pages)
        """
        total = query.count()
        total_pages = (total + per_page - 1) // per_page
        items = query.offset((page - 1) * per_page).limit(per_page).all()

        return items, total_pages

    @staticmethod
    def get_quotation_report_data() -> Dict[str, Any]:
        """Get data for quotation reports.
        
        Returns:
            Dictionary with quotation statistics for reports
        """
        quotations = Quotation.query.all()
        
        from collections import defaultdict
        status_counts = defaultdict(int)
        for q in quotations:
            status_counts[q.status] += 1

        return {
            'total': len(quotations),
            'by_status': dict(status_counts),
        }

    @staticmethod
    def get_user_access_logs(user_id: str, days: int = 30) -> List[Any]:
        """Get user access logs for specified period.
        
        Args:
            user_id: User ID
            days: Number of days to look back
            
        Returns:
            List of access log entries
        """
        from datetime import timedelta

        start_date = datetime.now() - timedelta(days=days)
        
        return AdminUser.query.filter(
            AdminUser.id == user_id,
            AdminUser.last_login_at >= start_date
        ).all()

    @staticmethod
    def calculate_revenue_analytics(start_date: datetime, end_date: datetime) -> Dict[str, Any]:
        """Calculate revenue analytics for date range.
        
        Args:
            start_date: Start date
            end_date: End date
            
        Returns:
            Dictionary with revenue analytics
        """
        from core.models.quotation import QuotationItem
        
        quotations = Quotation.query.filter(
            Quotation.created_at >= start_date,
            Quotation.created_at <= end_date
        ).all()

        total_revenue = sum(float(q.final_price or 0) for q in quotations)
        total_discount = sum(float(q.discount_pct or 0) for q in quotations)

        return {
            'total_revenue': Decimal(str(total_revenue)).quantize(Decimal('0.01')),
            'total_discount': Decimal(str(total_discount)),
        }
