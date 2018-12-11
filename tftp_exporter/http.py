"""
Web service for the Prometheus TFTP-exporter

Copyright 2018 Adobe. All rights reserved.
This file is licensed to you under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License. You may obtain a copy
of the License at http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software distributed under
the License is distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR REPRESENTATIONS
OF ANY KIND, either express or implied. See the License for the specific language
governing permissions and limitations under the License.
"""

from __future__ import print_function

import urlparse
from BaseHTTPServer import BaseHTTPRequestHandler
from BaseHTTPServer import HTTPServer
from SocketServer import ForkingMixIn
# import pprint
import prometheus_client
from prometheus_client import CONTENT_TYPE_LATEST

from tftp_collector import collect_tftp

from . import version

# pp = pprint.PrettyPrinter(indent=4)


class ForkingHTTPServer(ForkingMixIn, HTTPServer):
    """
    Forking class - to work with different Python-versions?
    """
    pass


class TftpExporterHandler(BaseHTTPRequestHandler):
    """
    TFTP Export Handler
    """

    def __init__(self, *args, **kwargs):
        # self._config_path = config_path
        BaseHTTPRequestHandler.__init__(self, *args, **kwargs)

    # noinspection PyPep8Naming
    def do_GET(self):
        """
        Function called with a GET-request.
        :return:
        """
        url = urlparse.urlparse(self.path)
        if url.path == '/metrics':
            params = urlparse.parse_qs(url.query)
            # pp.pprint(params)

            probe_target = None
            if 'target' not in params:
                self.send_response(400)
                self.end_headers()
                self.wfile.write("Missing 'target' from parameters")
                return
            else:
                probe_target = params['target'][0]
            if 'tftp_filename' in params:
                tftp_file = params['tftp_filename'][0]
            else:
                tftp_file = 'pxelinux.0'
            if 'tftp_port' in params:
                tftp_port_str = str(params['tftp_port'][0])
            else:
                tftp_port_str = '69'

            output = collect_tftp(host=probe_target, port_str=tftp_port_str, tftp_file=tftp_file)
            self.send_response(200)
            self.send_header('Content-Type', CONTENT_TYPE_LATEST)
            self.end_headers()
            self.wfile.write(output)
        elif url.path == '/':
            self.send_response(200)
            self.end_headers()
            self.wfile.write("""<html>
            <head><title>TFTP Exporter</title></head>
            <body>
            <h1>TFTP Exporter</h1>
            <p>Visit <code>/metrics?target=[hostname/IP-address]&tftp_filename=[tftp-file]</code> to use.</p>
            </body>
            </html>""")
        else:
            self.send_response(404)
            self.end_headers()


def start_http_server(port):
    """

    :param port:
    :return:
    """
    # handler = lambda *args, **kwargs: TftpExporterHandler(*args, **kwargs)
    def handler(*args, **kwargs):
        """

        :param args:
        :param kwargs:
        :return:
        """
        TftpExporterHandler(*args, **kwargs)

    server = ForkingHTTPServer(('', port), handler)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        server.shutdown()
