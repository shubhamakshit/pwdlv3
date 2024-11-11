from mainLogic.utils.glv import Global


class Endpoint:
    def __init__(self,
                 url=None,
                 method='GET',
                 headers=None,
                 payload=None,
                 files=None,
                 post_function=None,
                 ):

        if files is None:
            files = {}
        if payload is None:
            payload = {}
        if headers is None:
            headers = {}

        self.url = url
        self.method = method
        self.headers = headers
        self.payload = payload
        self.files = files
        self.post_function = post_function

    def __str__(self):
        return f'Endpoint(url={self.url}, method={self.method}, headers={self.headers}, payload={self.payload}, files={self.files}, post_function={self.post_function})'

    def __repr__(self):
        return self.__str__()

    def __dict__(self):
        return {
            'url': self.url,
            'method': self.method,
            'headers': self.headers,
            'payload': self.payload,
            'files': self.files,
            'post_function': self.post_function
        }

    def __eq__(self, other):
        if not isinstance(other, Endpoint):
            return False
        return self.__dict__ == other.__dict__

    def __ne__(self, other):
        return not self.__eq__(other)

    def __hash__(self):
        return hash(self.__str__())

    def __copy__(self):
        return Endpoint(
            url=self.url,
            method=self.method,
            headers=self.headers,
            payload=self.payload,
            files=self.files,
            post_function=self.post_function
        )

    def fetch(self):
        import requests
        response = requests.request(
            method=self.method,
            url=self.url,
            headers=self.headers,
            data=self.payload,
            files=self.files
        )

        # check if the response is valid and can be a json
        response_obj = None
        try:
            response_obj = response.json()
        except:
            response_obj = response.text
        finally:
            if self.post_function:
                if callable(self.post_function):
                    self.post_function(response_obj)
                else:
                    raise ValueError('post_function must be callable')

        return response_obj, response.status_code, response
