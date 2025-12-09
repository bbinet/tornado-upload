# -*- coding: utf-8 -*-
import mimetypes
import os
import logging
import re
import unicodedata
from datetime import datetime

import tornado.httpserver
import tornado.ioloop
import tornado.web
from tornado.options import define, options, parse_command_line
import filetype

define("port", default=8080, help="run on the given port", type=int)

UPLOAD_DIR = os.path.join(os.getcwd(), "uploaded")
PUBLIC_UPLOAD_DIR = os.path.join(UPLOAD_DIR, "public")
logging.info("UPLOAD_DIR={}, PUBLIC_UPLOAD_DIR={}".format(UPLOAD_DIR, PUBLIC_UPLOAD_DIR))
os.makedirs(UPLOAD_DIR, exist_ok=True)
os.makedirs(PUBLIC_UPLOAD_DIR, exist_ok=True)

def normalize_path(path: str) -> str:
    return re.sub(r"[^A-Za-z0-9_./-]", "",
            unicodedata.normalize("NFKD", path)
                .encode("ascii", "ignore").decode("ascii")
            ).strip("._")

def is_valid_name(s):
    if not isinstance(s, str): return False
    return re.match(r"^[a-z0-9_-]*$", s, re.IGNORECASE) is not None

def is_valid_nodeid(s):
    if not isinstance(s, str): return False
    return re.match(r"^[a-f0-9]{32}$", s, re.IGNORECASE) is not None

def is_safe_path(basedir, path, follow_symlinks=True):
    # resolves symbolic links
    if follow_symlinks:
        matchpath = os.path.realpath(path)
    else:
        matchpath = os.path.abspath(path)
    return basedir == os.path.commonpath((basedir, matchpath))

def write_safe_path(basedir, filepath, data):
    if not is_safe_path(basedir, filepath):
        logging.error("Unsafe path: %s \non basedir: %s", filepath, basedir)
        raise tornado.web.HTTPError(400)
    try:
        os.makedirs(os.path.dirname(filepath), exist_ok=True)
        with open(filepath, "wb") as f:
            f.write(data)
    except OSError as e:
        logging.error("Failed to write file due to OSError %s", str(e))
        raise

class UploadHandler(tornado.web.RequestHandler):
    def post(self):
        nodeid = self.get_argument("nodeid", default="")
        data = self.request.body
        kind = filetype.guess(data)
        prefix = self.get_query_argument("prefix", default="")
        subfolder = self.get_query_argument("subfolder", default="")
        extension = kind.extension if kind else mimetypes.guess_extension(self.request.headers.get('content-type'))
        if not (is_valid_nodeid(nodeid) and is_valid_name(prefix) and is_valid_name(subfolder) and extension):
            raise tornado.web.HTTPError(400)
        timestamp = datetime.today().strftime('%Y%m%d_%H%M%S')
        filename = "".join((prefix, timestamp, extension))
        y, m, d = datetime.today().strftime('%Y %m %d').split()
        filepath = normalize_path(os.path.normpath(os.path.join(
            UPLOAD_DIR, nodeid, subfolder, y, m, d, filename)))
        write_safe_path(UPLOAD_DIR, filepath, data)
        logging.info("{} uploaded {}, saved as {}".format(self.request.remote_ip, filename, filepath))
        self.write({"result": "upload OK"})

class PublicUploadHandler(tornado.web.RequestHandler):
    def post(self):
        data = self.request.body
        filepath = self.get_query_argument("filepath", default="")
        if not filepath:
            raise tornado.web.HTTPError(400, "Valid filepath required")
        filepath = normalize_path(os.path.normpath(os.path.join(PUBLIC_UPLOAD_DIR, *filepath.split("/"))))
        write_safe_path(PUBLIC_UPLOAD_DIR, filepath, data)
        logging.info("{} saved as {}".format(self.request.remote_ip, filepath))
        self.write({"result": "upload OK"})

def make_app():
    return tornado.web.Application(
        handlers=[
            (r"/", UploadHandler),
            (r"/public", PublicUploadHandler),
        ],
        template_path=os.path.join(os.getcwd(), "templates"),
        #debug=True,
        )

if __name__ == "__main__":
    options.parse_command_line()
    app = make_app()
    http_server = tornado.httpserver.HTTPServer(app)
    http_server.listen(options.port)
    tornado.ioloop.IOLoop.current().start()
