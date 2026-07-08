from flask import Blueprint, render_template

demo_start_bp = Blueprint('demo_start', __name__, template_folder='templates')


@demo_start_bp.route('/demo/start')
def demo_start():
    return render_template('demos/start.html')
