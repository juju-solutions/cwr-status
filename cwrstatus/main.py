from cwrstatus.config import app, ds

from cwrstatus.import_data import from_s3


@app.route('/')
def index():
    user = ds.db.users.find_one({'_id': 'id'})
    return 'hello {}'.format(user)


@app.route('/import-data')
def import_data():
    from_s3()
    return 'done.'


if __name__ == '__main__':
    app.run()
