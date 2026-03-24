from app.extensions import db

class Setting(db.Model):
    __tablename__ = 'settings'
    
    key = db.Column(db.String(50), primary_key=True)
    value = db.Column(db.Text, nullable=True)

    @staticmethod
    def get_value(key, default=None):
        setting = Setting.query.get(key)
        return setting.value if setting else default

    @staticmethod
    def set_value(key, value):
        setting = Setting.query.get(key)
        if not setting:
            setting = Setting(key=key)
            db.session.add(setting)
        setting.value = value
        db.session.commit()
