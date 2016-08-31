import os

from flask import (
    Response,
    render_template,
    send_from_directory,
)

from cwrstatus.config import app
from cwrstatus.datastore import S3


@app.route('/<path:fragment>')
def index(fragment):
    if fragment == 'favicon.ico':
        return send_from_directory(
            os.path.join(app.root_path, 'static/images'),
            'favicon.ico', mimetype='image/vnd.microsoft.icon')
    if fragment.endswith('.html'):
        mimetype = 'text/html; charset=utf-8'
    elif fragment.endswith('.json'):
        mimetype = 'application/json'
    else:
        return render_template('404.html', e='Page not found'), 404
    s3 = S3.factory(app.config['bucket_name'], app.config['prefix'])
    key = s3.get(fragment)
    if key is None:
        return render_template('404.html', e='Page not found'), 404
    return Response(key.get_contents_as_string(encoding='utf-8'),
                    mimetype=mimetype)


if __name__ == '__main__':
    app.run()
