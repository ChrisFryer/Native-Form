import uuid
from datetime import datetime, timezone

from app.extensions import db


class CloudConnection(db.Model):
    __tablename__ = 'cloud_connections'
    __table_args__ = (
        db.UniqueConstraint('user_id', 'name', name='uq_user_connection_name'),
    )

    id = db.Column(db.Uuid, primary_key=True, default=uuid.uuid4)
    user_id = db.Column(db.Uuid, db.ForeignKey('users.id'), nullable=True)
    name = db.Column(db.String(100), nullable=False)
    provider = db.Column(db.String(10), nullable=False)  # 'aws' or 'azure'
    is_default = db.Column(db.Boolean, nullable=False, default=False)
    credentials_encrypted = db.Column(db.Text, nullable=False)
    region = db.Column(db.String(50), nullable=True)
    is_active = db.Column(db.Boolean, nullable=False, default=True)
    last_tested = db.Column(db.DateTime, nullable=True)
    created_at = db.Column(
        db.DateTime, nullable=False,
        default=lambda: datetime.now(timezone.utc)
    )
    updated_at = db.Column(
        db.DateTime, nullable=False,
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc)
    )

    cached_resources = db.relationship(
        'CachedResource', backref='connection',
        lazy='dynamic', cascade='all, delete-orphan'
    )

    def set_credentials(self, credentials_dict):
        from app.utils.crypto import encrypt_credentials
        self.credentials_encrypted = encrypt_credentials(credentials_dict)

    def get_credentials(self):
        from app.utils.crypto import decrypt_credentials
        return decrypt_credentials(self.credentials_encrypted)

    def __repr__(self):
        return f'<CloudConnection {self.name} ({self.provider})>'
