from aiohttp import web
from aiohttp_wsgi import WSGIHandler

def make_aiohttp_app(app):
    wsgi_handler = WSGIHandler(app)
    aioapp = web.Application()
    aioapp.router.add_route('*', '/{path_info:.*}', wsgi_handler)
    return aioapp
