from twisted.internet import reactor
from twisted.web.resource import Resource
from binascii import unhexlify,hexlify

class WebInterface(Resource):
    def __init__(self, trackersessions):
        self.trackersessions = trackersessions 
    def render_GET(self,request):
        if request.path == "/":
            page = """
            <html>
            <head><title>pyratiomaster</title></head>
            <body>
            <form action='/modify' method='post'>
            <table>
            """
            ts = self.trackersessions.getAll()
            for k,v in ts.items():
                v.update()
                page += "<tr><td>Hostname: %s</td>" % v.hostname
                page += "<td>Info-hash: %s</td>" % hexlify(k).upper()
                page += "<td>Tracker-state: %s" % v.state
                page += "<td>Uploaded: %s</td>" % v.uploaded
                page += "<td>Rate: <input name='rate-%s' type='text' value='%s' /></td>" % (hexlify(k).upper(), v.rate)
                page += "</tr>"
            page += """
                    </table>
                    <input type='submit' name='submit-all' value='Submit' />
                    </form>
                    </body>
                    </html>
                    """
            return page
        return "bogus"
    def render_POST(self,request):
        if request.path == '/modify':
            if request.args.get('submit-all', False):
                all = self.trackersessions.getAll()
                for k,v in all.items():
                    v.setRate(  int(  request.args.get('rate-'+hexlify(k).upper() ,[0])[0]  ))
                request.redirect('/')
                return ""
