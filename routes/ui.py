from flask import render_template, Blueprint, redirect

from basic.annotations import login_required

routes = Blueprint('ui', __name__)


@routes.route('/', methods=['GET'])
@login_required
def root():
    return redirect(location='/ui/')


angular_files = ['styles', 'runtime', 'polyfills', 'main', 'favicon.ico']


@routes.route('/ui/', defaults={'path': ''}, methods=['GET'])
@routes.route('/ui/<path:path>', methods=['GET'])
@login_required
def ui_files(path: str):
    is_angular_file = len([x for x in angular_files if path.startswith(x)]) > 0
    if is_angular_file:
        return redirect(f'/static/{path}')
    else:
        return render_template('index.html')
