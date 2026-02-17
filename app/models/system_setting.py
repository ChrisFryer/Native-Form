from datetime import datetime, timezone

from app.extensions import db


class SystemSetting(db.Model):
    __tablename__ = 'system_settings'

    key = db.Column(db.String(100), primary_key=True)
    value = db.Column(db.Text, nullable=False)
    is_encrypted = db.Column(db.Boolean, nullable=False, default=False)
    updated_at = db.Column(
        db.DateTime, nullable=False,
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc)
    )

    @staticmethod
    def get(key, default=None):
        setting = db.session.get(SystemSetting, key)
        if setting is None:
            return default
        if setting.is_encrypted:
            from app.utils.crypto import decrypt_value
            return decrypt_value(setting.value)
        return setting.value

    @staticmethod
    def set(key, value, encrypted=False):
        if encrypted:
            from app.utils.crypto import encrypt_value
            store_value = encrypt_value(value)
        else:
            store_value = value

        setting = db.session.get(SystemSetting, key)
        if setting is None:
            setting = SystemSetting(
                key=key, value=store_value, is_encrypted=encrypted
            )
            db.session.add(setting)
        else:
            setting.value = store_value
            setting.is_encrypted = encrypted
        db.session.commit()

    def __repr__(self):
        return f'<SystemSetting {self.key}>'
