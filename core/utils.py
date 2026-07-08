"""Shared utilities for admin routes."""
from __future__ import annotations

from typing import Any
from flask import flash, redirect, render_template, request


def validate_form_fields(form_data: dict, required_fields: list[str]) -> list[str]:
    errors = []
    for field in required_fields:
        value = form_data.get(field)
        if not value:
            errors.append(f'{field} es requerido')
    return errors


def map_form_to_update_kwargs(form_data: dict, fields: list[str]) -> dict:
    return {field: form_data.get(field) for field in fields}


def get_paginated_results(query, page: int = 1, per_page: int = 10):
    total = query.count()
    total_pages = (total + per_page - 1) // per_page
    items = query.offset((page - 1) * per_page).limit(per_page).all()
    return items, total_pages


def build_statistics(context: dict) -> dict:
    stats = {}

    clients = context.get('clients', [])
    stats['clients'] = len(clients)

    projects = context.get('projects', [])
    stats['projects'] = len(projects)
    stats['active_projects'] = len([p for p in projects if p.status == 'active'])

    quotations = context.get('quotations', [])
    stats['quotations'] = len(quotations)
    stats['pending_quotations'] = len([q for q in quotations if q.status == 'draft'])

    return stats


def get_sorted_recent_items(query, limit: int = 5):
    """Apply limit to an already-ordered query and return all results."""
    return query.limit(limit).all()
