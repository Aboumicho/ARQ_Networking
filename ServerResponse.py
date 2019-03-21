
class ServerResponse:

    status_codes = {
        200: 'OK',
        404: 'Not Found'
    }

    def __init__(self,resp_code,resp_body):
        self.response_proto = 'HTTP/1.1'
        self.response_code = resp_code
        self.response_status_text = self.status_codes[resp_code]
        self.args = parser.parse_args()
        response_headers = {
                'Content-Type': 'text/html; encoding=utf8',
                'Content-Length': len(resp_body),
                'Connection': 'close',
            }

        self.response_headers_raw = ''.join('%s: %s\n' % (k, v) for k, v in \
                                                response_headers.items())
        
        self.response_body_raw = ''.join(resp_body)


    def send(self):
        if(self.args.verbose):
            return(str(self.response_proto) + '\n' + \
                str(self.response_code) + '\n' + \
                str(self.response_status_text) + '\n' + \
                str(self.response_headers_raw) + '\n' + \
                str(self.response_body_raw))
        else:
            return (
                str(self.response_body_raw))
                


if __name__ == '__main__':
    server = baseHTTPServer()
    server.bootServer()        