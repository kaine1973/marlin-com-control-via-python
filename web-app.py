import tomllib

from flask import Flask
from flask import render_template

from block.block_route import block_bp
from block.tablet_route import tablet_bp

app = Flask(__name__)
app.register_blueprint(block_bp)
app.register_blueprint(tablet_bp)
app.config.from_pyfile('settings.py')

from flask_bootstrap import Bootstrap5
bootstrap = Bootstrap5(app)


@app.route(rule="/")
def home():
    return render_template("index.html")


if __name__ == '__main__':
    app.run(host='192.168.3.100', port=5000)
