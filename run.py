from gamegraph import app
import os

port = int(os.environ.get('PORT', 5000))
app.secret_key = os.urandom(24)
app.run(host='0.0.0.0', port=port, debug=True)
