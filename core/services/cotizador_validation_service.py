"""Validation service for Cotizador operations."""
from __future__ import annotations

from typing import Dict, Any, Tuple
from decimal import Decimal

from core.errors import ValidationError


class CotizadorValidationService:
    """Handles validation logic for Cotizador operations."""

    @staticmethod
    def validate_calculate_request(data: Dict[str, Any]) -> Tuple[list[Dict[str, Any]], float]:
        """Validate calculation request data.
        
        Args:
            data: Request JSON data
            
        Returns:
            Tuple of (items, discount_percentage)
            
        Raises:
            ValidationError: If data is invalid
        """
        items = data.get('items', [])
        
        if not items:
            raise ValidationError('items is required and must not be empty')
        
        if not isinstance(items, list):
            raise ValidationError('items must be a list')
        
        try:
            items_list = []
            for idx, item in enumerate(items):
                if not isinstance(item, dict):
                    raise ValidationError(f'item at index {idx} must be a dictionary')
                
                required_fields = ['description', 'quantity', 'unit_price']
                for field in required_fields:
                    if field not in item:
                        raise ValidationError(f'item at index {idx} is missing required field: {field}')
                
                try:
                    quantity = int(item.get('quantity', 1))
                    if quantity <= 0:
                        raise ValidationError(f'item at index {idx}: quantity must be positive')
                except ValueError:
                    raise ValidationError(f'item at index {idx}: quantity must be an integer')
                
                try:
                    unit_price = float(item.get('unit_price', 0))
                    if unit_price < 0:
                        raise ValidationError(f'item at index {idx}: unit_price cannot be negative')
                except ValueError:
                    raise ValidationError(f'item at index {idx}: unit_price must be a valid number')
                
                items_list.append({
                    'description': item.get('description', ''),
                    'quantity': quantity,
                    'unit_price': unit_price,
                })
            
            discount_pct = float(data.get('discount_pct', 0))
            
            if discount_pct < 0 or discount_pct > 100:
                raise ValidationError('discount_pct must be between 0 and 100')
            
            return items_list, discount_pct
            
        except Exception as e:
            if isinstance(e, ValidationError):
                raise
            raise ValidationError(f'Error validating calculation data: {str(e)}')

    @staticmethod
    def validate_save_request(data: Dict[str, Any]) -> Dict[str, Any]:
        """Validate save request data.
        
        Args:
            data: Request JSON data
            
        Returns:
            Validated and sanitized request data
            
        Raises:
            ValidationError: If data is invalid
        """
        items = data.get('items', [])
        
        if not items:
            raise ValidationError('items is required and must not be empty')
        
        if not isinstance(items, list):
            raise ValidationError('items must be a list')
        
        try:
            items_list = []
            for idx, item in enumerate(items):
                if not isinstance(item, dict):
                    raise ValidationError(f'item at index {idx} must be a dictionary')
                
                if 'item_type' not in item:
                    raise ValidationError(f'item at index {idx} is missing required field: item_type')
                
                description = item.get('description', '')
                quantity = int(item.get('quantity', 1))
                unit_price = float(item.get('unit_price', 0))
                
                if quantity <= 0:
                    raise ValidationError(f'item at index {idx}: quantity must be positive')
                if unit_price < 0:
                    raise ValidationError(f'item at index {idx}: unit_price cannot be negative')
                
                items_list.append({
                    'item_type': item.get('item_type'),
                    'item_id': item.get('item_id'),
                    'description': description,
                    'quantity': quantity,
                    'unit_price': unit_price,
                })
            
            title = data.get('title', 'Cotización')
            if not title or not isinstance(title, str):
                raise ValidationError('title is required and must be a string')
            
            discount_pct = data.get('discount_pct', 0)
            if not isinstance(discount_pct, (int, float)) or discount_pct < 0 or discount_pct > 100:
                raise ValidationError('discount_pct must be a number between 0 and 100')
            
            return {
                'items': items_list,
                'title': title,
                'scope': data.get('scope', ''),
                'discount_pct': discount_pct,
                'client_id': data.get('client_id'),
            }
            
        except (ValueError, TypeError) as e:
            raise ValidationError(f'Error validating save data: {str(e)}')

    @staticmethod
    def validate_items_for_quantity(items: list[Dict[str, Any]]) -> Tuple[bool, str | None]:
        """Validate that all items have valid quantity.
        
        Args:
            items: List of items to validate
            
        Returns:
            Tuple of (is_valid, error_message)
        """
        for idx, item in enumerate(items):
            quantity = item.get('quantity')
            if quantity is None:
                return False, f'Item at index {idx} is missing quantity'
            
            try:
                quantity = int(quantity)
                if quantity <= 0:
                    return False, f'Item at index {idx}: quantity must be positive'
            except ValueError:
                return False, f'Item at index {idx}: quantity must be an integer'
        
        return True, None
