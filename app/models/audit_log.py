import uuid
from datetime import datetime, timezone

from app.extensions import db


class AuditLog(db.Model):
    __tablename__ = 'audit_log'
    __table_args__ = (
        db.Index('idx_audit_log_user', 'user_id', 'created_at'),
    )

    id = db.Column(db.Uuid, primary_key=True, default=uuid.uuid4)
    user_id = db.Column(db.Uuid, db.ForeignKey('users.id'), nullable=True)
    action = db.Column(db.String(100), nullable=False)
    target_type = db.Column(db.String(50), nullable=True)
    target_id = db.Column(db.Uuid, nullable=True)
    details = db.Column(db.JSON, nullable=True)
    ip_address = db.Column(db.String(45), nullable=True)
    created_at = db.Column(
        db.DateTime, nullable=False,
        default=lambda: datetime.now(timezone.utc)
    )

    def __repr__(self):
        return f'<AuditLog {self.action} by {self.user_id}>'
