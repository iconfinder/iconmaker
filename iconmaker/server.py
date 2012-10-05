# -*- coding: utf-8 -*-

#
# front end for generating ICO/ICNS files
#
import flask
from converter import Converter
import json

app = flask.Flask(__name__)
app.debug = True


@app.route("/")
def index():
    return "IconMaker 1.0"


# input: icon id
# output: output ICO/ICNS file directly (or give its URL)
# sample request: 	http://localhost:5000/convert_icon/ico/1/raw
#					http://localhost:5000/convert_icon/ico/1/json
@app.route("/convert_icon/<format>/<int:icon_id>/<output_format>")
def convert_icon(format, icon_id, output_format):
	# get the urls for all the sizes of this icon
	# generate a new collection icon (ICO or ICNS)

	# check our input
	# and maybe send invalid error code, etc
	if format not in ['ico', 'icns']:
		flask.abort(404)

	if output_format not in ['raw', 'json', 'xml']:
		flask.abort(404)

	# get all the icon url(s) for this icon id
	# xxx: should be a controller here that gets data from some model (ie datasource)
	icons_remote = [
					'http://localhost/www/icon16x16.png',
					'http://localhost/www/icon32x32.png',
					'http://localhost/www/icon48x48.png',
					]
	converter = Converter(icons_remote)

	# dynamically call the conversion method at runtime
	method_name = getattr(converter, 'to_%s' % format)
	output_path = method_name()

	# either directly send the output_path as data
	# or upload the icon to our CDN and send the final url
	if output_format == 'raw':
 		#resp = flask.make_response(open(output_path).read())
 	   	#resp.content_type = "image/%s" % format
 	   	return flask.send_file(output_path, mimetype='image/%s' % format)

	if output_format == 'json':
		return json.dumps({'output_path': str(output_path)})


if __name__ == "__main__":
    app.run()
