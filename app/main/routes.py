from app.main.logic import *
from app.thumbnail import thumb
from app.main import bp
from flask import redirect, render_template, flash, request, make_response, session, url_for, current_app, Response
from flask import send_from_directory
from datetime import datetime


def render_template2(path, **args):
    return render_template(path, **args, logged_in=session.get('logged_in'))


def logged_in():
    ret = False
    current_app.logger.info(f'session: {id(session)} {session}')
    # current_app.logger.info(f'session["logged_in"] = {session.get("logged_in")}')
    # current_app.logger.info(f'secret key: {current_app.config["SECRET_KEY"]}')
    t_logged_in = session.get('logged_in')
    if t_logged_in:
        ago_s = (datetime.utcnow() - t_logged_in).seconds
        current_app.logger.info(f'Admin is logged in and was active {ago_s//60}m {ago_s%60}s ago')
        if ago_s < 20 * 60:  # 20min #TODO move to config
            session['logged_in'] = datetime.utcnow()
            ret = True
    if not ret:
        current_app.logger.info('Clearing session["logged_in"]')
        if 'logged_in' in session:
            del session['logged_in']
    return ret


# @bp.after_request
# def after_request(response):
#    current_app.logger.info(f'session["logged_in"]: {session.get("logged_in")}')
#    return response


@bp.route('/robots.txt')
def robots_txt():
    r = Response(render_template('robots.txt'))
    r.headers = {'content-type': 'text/plain'}
    return r


@bp.route('/sitemap.xml')
def sitemap():
    return send_from_directory('static/content', 'sitemap.xml')


@bp.route('/favicon.ico')
def favicon():
    return send_from_directory('static/img/favicon', 'favicon.ico')


@bp.route('/')
def index():
    visitor = None

    '''last_cat = get_last_cat()
    if last_cat:
        current_app.logger.info(f'Deleting {last_cat}')
        db.session.delete(last_cat)
        db.session.commit()'''

    prev = False
    etag = request.args.get('prev')
    if etag:
        prev = True
    else:
        etag = next((x[1] for x in request.headers if x[0].lower() == 'if-none-match'), None)
        if not etag:
            modified = next((x[1] for x in request.headers if x[0].lower() == 'if-modified-since'), None)
            if modified:
                current_app.logger.debug(f'Getting if-modified-since: {modified}')
                etag = get_etag(modified)

        # current_app.logger.debug(f'Headers: {request.headers}')

    balloon = None

    current_app.logger.debug(f'ETag: {etag}')
    if etag:
        visitor = get_visitor(etag)
    if not visitor:
        remote_addr = request.environ.get('HTTP_X_REAL_IP', request.remote_addr)
        visitor = create_visitor(remote_addr)
        locale = request.accept_languages.best_match(current_app.config['LANGUAGES'])
        balloon = get_greeting_balloon(locale)
    # accept-language: ru-RU,ru;q=0.9,en-US;q=0.8,en;q=0.7

    if prev:
        cat = get_previous_cat(visitor.last_cat_idx)
        visitor.last_cat_idx = cat.index
        cat = get_previous_cat(visitor.last_cat_idx)  # twice because of redirect that increments index
        visitor.last_cat_idx = cat.index
    else:
        cat = get_next_cat(visitor.last_cat_idx)

    current_app.logger.info(f'Visitor #{visitor.id} {visitor.etag}: last seen: {visitor.last_cat_idx}; now showing {cat.index}')

    visitor.t_last_seen = datetime.now()
    visitor.last_cat_idx = cat.index
    db.session.commit()

    # flash('This is a public service announcement, this is only a test.', category='error')
    if prev:
        return redirect(url_for('main.index'))
    r = make_response(render_template2('index.htm', visitor=visitor, cat=cat, balloon=balloon))
    r.headers.set('ETag', visitor.etag)
    r.headers.set('Cache-Control', 'max-age=0, private')
    r.headers.set('Last-Modified', f'Thu, 10 Dec 2020 {visitor.get_mod_time()} GMT')

    current_app.logger.debug(f'Set last modified: {visitor.get_mod_time()}')
    # current_app.logger.debug(f'Headers: {r.headers}')
    return r


@bp.route('/logout')
def logout():
    if 'logged_in' in session:
        del session['logged_in']
    current_app.logger.info(f'Admin logged out at {datetime.now()}')
    return redirect(url_for('main.index'))


@bp.route('/login', methods=['GET', 'POST'])
def login():
    if logged_in():
        return redirect(url_for('main.admin'))
    if request.form:
        username = request.form.get('username')
        password = request.form.get('password')
        if verify_password(username, password):
            session['logged_in'] = datetime.utcnow()
            current_app.logger.info(f'Auth of `{username}:{password}` from {request.remote_addr} '
                                    f'succeeded at {datetime.now()}')
            return redirect(url_for('main.admin'))
        else:
            current_app.logger.warning(f'Auth of `{username}:{password}` failed')
            flash('invalid username or password', category='error')
    return render_template2('login.htm', title='Вход')


@bp.route('/admin', methods=['GET', 'POST'])
def admin():
    if logged_in():
        if request.form:
            try:
                process_cat_form(request.form.to_dict())
            except RuntimeError as ex:
                current_app.logger.error(f'Processing admin form failed: {str(ex)}')
                current_app.logger.exception(ex)
                flash(str(ex), category='error')
            return redirect(url_for('main.admin'))

        cats = models.Cat.query.order_by(models.Cat.index).all()
        return render_template2('admin.htm', title='Admin page', cats=cats, thumb=thumb)
    return redirect(url_for('main.login'))


# @bp.app_errorhandler(404)
# def handle_404(err):
#    return redirect(url_for('main.index'))

# ETag idea: https://habr.com/en/company/edison/blog/509484/
