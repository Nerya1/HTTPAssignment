from Bottle import Bottle, RequestError, File
from pathlib import Path

bottle = Bottle("127.0.0.1", 8080)

source_path = Path('src/')
extension_matching = {
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
    return File('src/index.html'), extension_matching['html']


@bottle.route("/calculate-next")
def calculate_next(route, num='1'):
    return str(int(num) + 1), ''


@bottle.route("/calculate-area")
def calculate_area(route, width='1', height='1'):
    return str(int(int(width) * int(height) / 2))


@bottle.route("/*.*")
def get_file(route):
    file_path = source_path / Path(route[1:])

    if source_path in file_path.parents and file_path.exists():
        return File(file_path), extension_matching[route.split('.')[-1]]

    raise RequestError("403 Forbidden", "requested file is out of source path")


if __name__ == '__main__':
    bottle.run()
