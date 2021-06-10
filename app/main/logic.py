from app import db, models
import base64
import re
from sqlalchemy import and_, desc
from sqlalchemy.sql.expression import func
from flask import flash, current_app, session
from werkzeug.security import check_password_hash


def verify_password(username: str, password: str) -> bool:
    """Verify password correctness.
    Args:
        username (str): User login.
        password (str): User password.
    Returns:
        True if password is valid.
    """
    root = current_app.config['ROOT']
    if root is None:
        return True
    if username == root:
        if check_password_hash(current_app.config['ROOT_PASSWORD'], password):
            session['logged_in'] = True
            return True
    return False


def _generate_etag(s: str) -> str:
    """Generate unique ID string for user.
    Args:
        s (str): Input string, mostly user id in `xx:xx:xx` format.
    Returns:
        Unique ID.
    """
    try:
        return base64.b64encode(s.encode()).decode('ascii')
    except RuntimeError:
        pass


def get_etag(s: str) -> str:
    """Generate unique ID string for user.
    Args:
        s (str): Input string, mostly value of HTTP header `If-Modified-Since`.
    Returns:
        Unique ID.
    """
    m = re.search('(\\d{2}:\\d{2}:\\d{2})', s)
    if m:
        time = m[0]
        return _generate_etag(time)


def get_visitor(etag: str) -> models.Visitor:
    """Find visitor by unique ID.
    Args:
        etag (str): Unique ID.
    Returns:
        Existing visitor or None.
    """
    visitor = models.Visitor.query.filter(etag == models.Visitor.etag).first()
    return visitor


def create_visitor(remote_addr: str) -> models.Visitor:
    """Create new visitor or return existing in case of DOS/DDOS.
    Args:
        remote_addr (str): User remote address (IP).
    Returns:
        New visitor or existing one in case of DOS/DDOS.
    """
    # TODO max visitors count to config
    over_limit = models.Visitor.query.order_by(desc(models.Visitor.t_last_seen)).limit(1).offset(100).first()
    if over_limit:
        del_over_limit = models.Visitor.__table__.delete().where(models.Visitor.t_last_seen >= over_limit.t_last_seen)
        db.session.execute(del_over_limit)
        db.session.commit()

    # TODO max visitors count with same IP to config
    neighbours = models.Visitor.query\
        .filter(models.Visitor.remote_addr == remote_addr)\
        .order_by(models.Visitor.t_last_seen)\
        .all()
    if len(neighbours) >= 4:
        visitor = neighbours[0]
        current_app.logger.info(f'Using known visitor from {remote_addr} with ETag {visitor.etag}')
        return visitor

    visitor = models.Visitor()
    visitor.last_cat_idx = -1
    visitor.remote_addr = remote_addr
    db.session.add(visitor)
    db.session.commit()

    visitor.etag = _generate_etag(visitor.get_mod_time())
    db.session.add(visitor)

    current_app.logger.info(f'Creating visitor with ETag {visitor.etag}')
    return visitor


def get_random_cat() -> models.Cat:
    """Get random cat from database."""
    return models.Cat.query.filter(models.Cat.disabled == False).order_by(func.random()).first()


def get_first_cat() -> models.Cat:
    """Get cat with minimal view index from database."""
    return models.Cat.query.filter(models.Cat.disabled == False).order_by(models.Cat.index).first()


def get_next_cat(last_index: int) -> models.Cat:
    """Get next cat.
    Args:
        last_index (int): View index of last seen cat.
    """
    cat = None
    if last_index != -1:
        cat = models.Cat.query.filter(and_(models.Cat.disabled == False, models.Cat.index > last_index)).order_by(
            models.Cat.index).first()
    if cat is None:
        cat = get_first_cat()
    return cat


def get_last_cat() -> models.Cat:
    """Get cat with maximal view index from database."""
    return models.Cat.query.filter(models.Cat.disabled == False).order_by(desc(models.Cat.index)).first()
    # and_(models.Cat.disabled == False, models.Cat.index >= 0)).first()


def get_previous_cat(last_index: int) -> models.Cat:
    """Get previous cat.
    Args:
        last_index (int): View index of last seen cat.
    """
    cat = models.Cat.query.filter(and_(models.Cat.disabled == False, models.Cat.index < last_index)).order_by(
        desc(models.Cat.index)).first()
    if cat is None:
        cat = get_last_cat()
    return cat


def process_cat_form(form):
    """Process admin form with cats data.
    Args:
        form: Data from HTTP POST request.
    """
    new_cat = None

    indices = {}
    enabled = {}

    for rec in form:
        if rec.startswith('cat'):
            underscore_idx = rec.index('_')
            if underscore_idx > 3:
                cat_id = rec[3:underscore_idx]
                param = rec[underscore_idx + 1:]
                value = form[rec]
                if cat_id == 'new':
                    if param == 'url':
                        new_cat = value
                    # elif param == 'idx':
                    #    new_cat_idx = int(value)
                else:
                    cat_id = int(cat_id)
                    if param == 'idx':
                        indices[cat_id] = int(value)
                    elif param == 'enabled':
                        enabled[cat_id] = (value == 'on')

    cats = models.Cat.query.all()
    for cat in cats:
        if cat.id in indices:
            cat.index = indices[cat.id]
        cat.disabled = cat.id not in enabled
        db.session.add(cat)

    if new_cat:
        existing_cat = next((cat for cat in cats if cat.url == new_cat), None)
        if not existing_cat:
            cat = models.Cat(index=len(cats),
                             url=new_cat,
                             disabled=False)
            db.session.add(cat)
            current_app.logger.info(f'New picture {new_cat} added')
        else:
            current_app.logger.warning(f'Picture {new_cat} is already known')
            flash('This picture is already known', category='error')

    db.session.commit()


def get_greeting_balloon(locale: str) -> str:
    """Return text of greeting balloon for first visit.
    Args:
        locale (str): Visitor locale. The only applicable value is `ru`.
    """
    if locale == 'ru':
        return '''Обновите страницу или нажмите пробел или кнопку «👉»,
            чтобы увидеть следующее изображение; нажмите «👈», чтобы увидеть предыдущее.<br />
            Наслаждайтесь!<br />
            <br />
            С уважением, Алёшка🐾.'''
    return '''Refresh page or use spacebar or “👉” button to see next picture,
        “👈” to see previous.<br />
        Enjoy!<br />
        <br />
        Sincerely yours, Alёshka🐾.'''
