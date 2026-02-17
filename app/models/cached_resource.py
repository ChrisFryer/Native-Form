import uuid
from datetime import datetime, timezone

from app.extensions import db


class CachedResource(db.Model):
    __tablename__ = 'cached_resources'
    __table_args__ = (
        db.Index('idx_cached_resources_type', 'connection_id', 'resource_type'),
        db.Index('idx_cached_resources_discovered', 'discovered_at'),
    )

    id = db.Column(db.Uuid, primary_key=True, default=uuid.uuid4)
    connection_id = db.Column(
        db.Uuid, db.ForeignKey('cloud_connections.id'), nullable=False
    )
    resource_type = db.Column(db.String(100), nullable=False)
    resource_id = db.Column(db.String(256), nullable=False)
    resource_name = db.Column(db.String(256), nullable=True)
    region = db.Column(db.String(50), nullable=True)
    raw_data = db.Column(db.JSON, nullable=False)
    discovered_at = db.Column(
        db.DateTime, nullable=False,
        default=lambda: datetime.now(timezone.utc)
    )

    def __repr__(self):
        return f'<CachedResource {self.resource_type}:{self.resource_id}>'
