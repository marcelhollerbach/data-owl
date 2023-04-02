

def init_routes(app):
    from routes.auth import routes as auth_routes
    from routes.ui import routes as ui_routes
    from routes.v1.de import routes as de_routes
    from routes.v1.dtm import routes as dtm_routes
    from routes.v1.search_routes import routes as search_routes

    app.register_blueprint(de_routes, url_prefix='/v1')
    app.register_blueprint(dtm_routes, url_prefix='/v1')
    app.register_blueprint(search_routes, url_prefix='/v1')
    app.register_blueprint(auth_routes)
    app.register_blueprint(ui_routes)
