from flask import Flask
from config import Config

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    # 注册蓝图
    from routes.api import bp as api_bp
    app.register_blueprint(api_bp)

    from routes.search import bp as search_bp
    app.register_blueprint(search_bp)

    from routes.config import bp as config_bp
    app.register_blueprint(config_bp)

    return app

if __name__ == '__main__':
    app = create_app()
    app.run(debug=True, host='0.0.0.0', port=5000)