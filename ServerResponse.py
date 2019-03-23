

class ServerRequest:
    def __init__(self, request):
        self.method = None
        self.uri = None
        self.http_version = '1.0'
        self.headers = {}

        self.parse(request)
    
    def parse(self,data):
        splitData = data.decode('utf-8').split(' ')
        self.method = splitData[0]
        self.uri = splitData[1]


class ServerResponse:

    status_codes = {
        200: 'OK',
        404: 'Not Found'
    }

    def __init__(self,resp_code,resp_body):
        self.response_proto = 'HTTP/1.1'
        self.response_code = resp_code
        self.response_status_text = self.status_codes[resp_code]
        response_headers = {
                'Content-Type': 'text/html; encoding=utf8',
                'Content-Length': len(resp_body),
                'Connection': 'close',
            }

        self.response_headers_raw = ''.join('%s: %s\n' % (k, v) for k, v in \
                                                response_headers.items())
        
        self.response_body_raw = ''.join(resp_body)


    def send(self):
        return(str(self.response_proto) + '\n' + \
                str(self.response_code) + '\n' + \
                str(self.response_status_text) + '\n' + \
                str(self.response_headers_raw) + '\n' + \
                str(self.response_body_raw))
                
