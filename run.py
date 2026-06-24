import gevent.monkey
gevent.monkey.patch_all()

import os
from app import create_app, socketio

app = create_app()

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    socketio.run(app, host='0.0.0.0', port=port, debug=True, use_reloader=False, allow_unsafe_werkzeug=True)
