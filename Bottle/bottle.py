from functools import wraps
from socket import create_server
from select import select
from re import compile
from traceback import format_exc

from Bottle import Protocol, RequestError


def render_route(func, *args, **kwargs):
    result = func(
        *args,
        **{key: value for key, value in kwargs.items() if key in func.__code__.co_varnames}
    )

    try:
        return Protocol.pack(result[0]), result[1]

    except IndexError:
        return Protocol.pack(result), None


class Bottle:
    def __init__(self, host: str, port: int):
        self.running = True

        self.socket = create_server((host, port))
        self.socket.settimeout(Protocol.TIMEOUT)
        self.socket.listen()

        self.clients = {}
        self.routes = {
            'GET': {},
            'POST': {},
        }

    def route(self, route: str, method='GET'):
        if method not in self.routes.keys():
            raise KeyError(f'Method {method} not supported')

        def decorator(func):
            @wraps(func)
            def wrap(*args, **kwargs):
                header = "HTTP/1.1 {status}\r\n" \
                         "Connection: keep-alive\r\n" \
                         "Content-Type: {type}\r\n" \
                         "Content-Length: {length}\r\n\r\n"

                status = '200 OK'

                try:
                    response, type_ = render_route(func, *args, **kwargs)

                except RequestError as e:
                    response = Protocol.pack(e.response)
                    type_ = e.type
                    status = e.status_code

                except TypeError:
                    response = b'illegal parameter'
                    type_ = 'text/plain; charset=utf-8'
                    status = '403 Forbidden'

                if type_ is None:
                    type_ = 'text/html; charset=utf-8'

                return (
                    header.format(
                        status=status,
                        type=type_,
                        length=len(response)
                    ).encode() +
                    response
                )

            self.routes[method].update({compile(route): wrap})
            return wrap

        return decorator

    def handle_request(self, request):
        request = Protocol.process_request(request)
        match request:
            case {'Method': method, 'Route': requested_route, 'Variables': kwargs}:
                for route, func in self.routes[method].items():
                    if route.fullmatch(requested_route):
                        if method == 'POST':
                            return func(requested_route, **kwargs, content=request['Content'])

                        else:
                            return func(requested_route, **kwargs)

        return b''

    def accept(self):
        connection, address = self.socket.accept()

        self.clients.update({
            connection: address
        })

    def respond(self):
        ins, outs, errs = select(
            self.clients.keys(),
            (),
            (),
            0.1
        )

        for client in ins:
            data, received = Protocol.receive(client)

            if received:
                if data:
                    client.send(self.handle_request(data))

                else:
                    self.clients.pop(client)

    def run(self):
        while self.running:
            try:
                self.accept()

            except TimeoutError:
                pass

            try:
                self.respond()

            except Exception as e:
                print(f'{e}\r\n{format_exc()}\r', end='')
