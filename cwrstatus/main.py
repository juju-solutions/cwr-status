from cwrstatus.config import app, ds

from datastore import Datastore


@app.route('/')
def index():
    data = Datastore(app)
    user = ds.db.users.find_one({'_id': 'id'})
    user = data.ds.db.users.find_one({'dd': 'dd'})
    return 'hello {}'.format(user)


if __name__ == '__main__':
    app.run()
