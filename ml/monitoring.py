from flask import Flask
from prometheus_client import Counter
from prometheus_client import start_http_server, make_wsgi_app
from werkzeug.middleware.dispatcher import DispatcherMiddleware

c = Counter('my_failures', 'Description of counter')
c.inc()     # Increment by 1
c.inc(1.6)  # Increment by given value

app = Flask(__name__)

# Add prometheus wsgi middleware to route /metrics requests
app.wsgi_app = DispatcherMiddleware(app.wsgi_app, {
    '/metrics': make_wsgi_app()
})
if __name__ == "__main__":
    app.run(port=8000)