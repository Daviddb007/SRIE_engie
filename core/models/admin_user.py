from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from core import db, login_manager
from core.models.base import BaseModel


class AdminUser(BaseModel, UserMixin):
    __tablename__ = 'admin_users'

    email = db.Column(db.String(255), nullable=False, unique=True)
    password_hash = db.Column(db.String(512), nullable=False)
    full_name = db.Column(db.String(255), nullable=False)
    role = db.Column(db.String(20), nullable=False, default='editor')
    is_active_ = db.Column('is_active', db.Boolean, nullable=False, default=True)
    last_login_at = db.Column(db.DateTime(timezone=True))

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    @property
    def is_active(self):
        return self.is_active_

    def __repr__(self):
        return f'<AdminUser {self.email}>'


@login_manager.user_loader
def load_user(user_id):
    return AdminUser.query.get(user_id)
