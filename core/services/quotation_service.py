"""Service layer for Quotation operations."""
from __future__ import annotations

from datetime import datetime, timezone, timedelta

from core import db
from core.errors import NotFoundError, ValidationError
from core.models.quotation import Quotation, QuotationItem
from core.models.client import Client


class QuotationService:
    """Handles all quotation business logic."""

    @staticmethod
    def get_all() -> list[Quotation]:
        return Quotation.query.order_by(Quotation.created_at.desc()).all()

    @staticmethod
    def get_by_id(quotation_id: str) -> Quotation:
        q = Quotation.query.get(quotation_id)
        if not q:
            raise NotFoundError(f'Quotation {quotation_id} not found')
        return q

    @staticmethod
    def calculate(items: list[dict], discount_pct: float = 0) -> dict:
        """Calculate quotation totals from items."""
        total = sum(
            float(item.get('unit_price', 0)) * int(item.get('quantity', 1))
            for item in items
        )
        discount = total * (discount_pct / 100)
        return {'total': total, 'discount': discount, 'final': total - discount}

    @staticmethod
    def create(
        client_id: str,
        title: str,
        items: list[dict],
        scope: str = '',
        discount_pct: float = 0,
        created_by: str | None = None,
    ) -> Quotation:
        """Create a quotation with items."""
        if not client_id:
            raise ValidationError('Selecciona un cliente')

        client = Client.query.get(client_id)
        if not client:
            raise NotFoundError(f'Client {client_id} not found')

        totals = QuotationService.calculate(items, discount_pct)

        quotation = Quotation(
            quotation_number=Quotation.generate_number(),
            client_id=client_id,
            created_by=created_by,
            status='draft',
            title=title,
            scope=scope,
            total_price=totals['total'],
            discount_pct=discount_pct,
            final_price=totals['final'],
            valid_until=datetime.now(timezone.utc).date() + timedelta(days=30),
        )
        db.session.add(quotation)
        db.session.flush()

        for idx, item in enumerate(items):
            qi = QuotationItem(
                quotation_id=quotation.id,
                item_type=item.get('item_type', 'custom'),
                item_id=item.get('item_id'),
                description=item.get('description', ''),
                quantity=int(item.get('quantity', 1)),
                unit_price=float(item.get('unit_price', 0)),
                total_price=float(item.get('unit_price', 0)) * int(item.get('quantity', 1)),
                sort_order=idx,
            )
            db.session.add(qi)

        db.session.commit()
        return quotation
