
class BankiException(Exception):
    code = None
    description = None

    def __init__(self, code=500, description=None):
        self.code = code
        self.description = description

    def to_dict(self):
        return {'code': self.code, 'description': self.description}



class RemoteBankiException(BankiException):
    inner_exception = None
    request_object = None

    def __init__(self, inner_exception, request_object):
        self.inner_exception = inner_exception
        self.request_object = request_object
        self.code = 500
        self.description = "A problem with remote server!"



