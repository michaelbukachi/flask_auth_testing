from flask import Flask, request, redirect, url_for
from flask_login import LoginManager, UserMixin, login_required, login_user, logout_user
from werkzeug.exceptions import MethodNotAllowed, Unauthorized


class Config:
    SECRET_KEY = 'Some very long secret key'


class User(UserMixin):
    pass


login_manager = LoginManager()


@login_manager.user_loader
def user_loader(email):
    if email != 'test@gmail.com':
        return

    user = User()
    user.id = email
    return user


@login_manager.request_loader
def request_loader(request):
    email = request.form.get('email')
    if email != 'test@gmail.com':
        return

    user = User()
    user.id = email

    user.is_authenticated = request.form['password'] == 'test'

    return user


@login_manager.unauthorized_handler
def unauthorized_handler():
    raise Unauthorized()


def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    login_manager.init_app(app)

    @app.route('/')
    @login_required
    def index():
        return 'Ok'

    @app.route('/login', methods=['GET', 'POST'])
    def login():
        if request.method != 'POST':
            raise MethodNotAllowed()

        if request.form['email'] == 'test@gmail.com' and request.form['password'] == 'test':
            user = User()
            user.id = request.form['email']
            login_user(user)
            return redirect(url_for('.index'))

        raise Unauthorized()

    @app.route('/logout')
    def logout():
        logout_user()
        return 'Logged out'

    return app
