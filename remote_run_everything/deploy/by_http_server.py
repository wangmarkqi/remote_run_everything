import cherrypy
from remote_run_everything.deploy.by_http_tool import ByHttpTool
from remote_run_everything.tools.common import Common

from cherrypy.process.plugins import Daemonizer


def cherrypy_in_daemon(myapp, port, prefix):
    cherrypy.config.update({
        "server.socket_port": port,
    })
    Daemonizer(cherrypy.engine).subscribe()
    cherrypy.tree.mount(myapp(), prefix)
    cherrypy.engine.start()
    cherrypy.engine.block()


class ByHttpServer:

    @cherrypy.expose
    @cherrypy.tools.json_out()
    @cherrypy.tools.json_in()
    def readb64(self):
        try:
            args = cherrypy.request.json
            path = args['path']
            data = Common().readb64(path)
            return {"status": "ok", "data": data}
        except Exception as e:
            return {"status": "fail", "data": str(e)}

    @cherrypy.expose
    @cherrypy.tools.json_out()
    @cherrypy.tools.json_in()
    def dep_writeb64(self):
        try:
            args = cherrypy.request.json
            path = args['path']
            b64 = args['b64']
            Common().writeb64(path, b64)
            return {"status": "ok", "data": path}
        except Exception as e:
            return {"status": "fail", "data": str(e)}

    @cherrypy.expose
    @cherrypy.tools.json_out()
    @cherrypy.tools.json_in()
    def iterdir(self):
        try:
            args = cherrypy.request.json
            root = args['root']
            disallow = args.get("disallow_keys", [])
            data = ByHttpTool().all_local_path(root, disallow)
            return {"status": "ok", "data": data}
        except Exception as e:
            return {"status": "fail", "data": str(e)}
