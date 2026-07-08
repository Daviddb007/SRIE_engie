"""Domain enums — replaces magic strings throughout the codebase."""
import enum


class SystemType(str, enum.Enum):
    """Sistema Digital tier."""
    START = 'start'
    GROWTH = 'growth'
    INTELLIGENCE = 'intelligence'


class ProjectStatus(str, enum.Enum):
    """Project lifecycle status."""
    DRAFT = 'draft'
    ACTIVE = 'active'
    PAUSED = 'paused'
    COMPLETED = 'completed'
    CANCELLED = 'cancelled'


class UserRole(str, enum.Enum):
    """Admin user roles."""
    SUPER_ADMIN = 'super_admin'
    ADMIN = 'admin'
    EDITOR = 'editor'


class QuotationStatus(str, enum.Enum):
    """Quotation lifecycle status."""
    DRAFT = 'draft'
    SENT = 'sent'
    VIEWED = 'viewed'
    ACCEPTED = 'accepted'
    REJECTED = 'rejected'
