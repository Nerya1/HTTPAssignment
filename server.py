from Bottle import Bottle, RequestError, File
from pathlib import Path

bottle = Bottle("127.0.0.1", 8080)

source_path = Path('src/')
extension_matcher = {
    'txt': 'text/plain; charset=utf-8',
    'html': 'text/html; charset=utf-8',
    'js': 'text/javascript; charset=utf-8',
    'jpg': 'image/jpeg',
    'ico': 'image/x-icon',
    'png': 'image/png',
    'css': 'text/css',
    'gif': 'image/gif',
}


@bottle.route("/")
def index(route):
    return File('src/index.html'), extension_matcher['html']


@bottle.route("/calculate-next")
def calculate_next(route, num='1'):
    return int(num) + 1, ''


@bottle.route("/calculate-area")
def calculate_area(route, width='1', height='1'):
    return int(width) * int(height) / 2


@bottle.route("/*.*")
def get_file(route):
    file_path = source_path / route[1:]

    if source_path not in file_path.parents:
        raise RequestError("403 Forbidden", "Requested file is out of source path")

    if not file_path.is_file():
        raise RequestError("404 Not Found", "Requested file not found")

    return File(file_path), extension_matcher[route.split('.')[-1]]


@bottle.route('/upload', method='POST')
def post(route, file_name=None, content=None):
    file_path = source_path / 'uploads' / file_name

    if source_path not in file_path.parents:
        raise RequestError("403 Forbidden", "Can't save files out of source folder")

    with open(file_path, 'wb') as f:
        f.write(content)


if __name__ == '__main__':
    bottle.run()
