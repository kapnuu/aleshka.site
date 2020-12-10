from app import db

__author__ = 'kapnuu'


class Visitor(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    etag = db.Column(db.String(32), index=True)
    remote_addr = db.Column(db.String(16), index=True)
    t_last_seen = db.Column(db.DateTime)
    last_cat_idx = db.Column(db.Integer, default=-1)
    # deleted = db.Column(db.Boolean, default=False)

    def get_mod_time(self) -> str:
        s = self.id % 60
        m = self.id // 60 % 60
        h = self.id // 60 // 60
        return f'{h:02}:{m:02}:{s:02}'


class Cat(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    index = db.Column(db.Integer, index=True)
    url = db.Column(db.String(320))
    disabled = db.Column(db.Boolean, default=False)


class Thumbnail(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    cat_id = db.Column(db.Integer, unique=True, index=True)
    data = db.Column(db.BLOB)
    width = db.Column(db.Integer)
