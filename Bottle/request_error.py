class RequestError(BaseException):
    def __init__(self, status_code, response, type_='text/plain; charset=utf-8'):
        self.status_code = status_code
        self.response = response
        self.type = type_

        super().__init__(status_code)
