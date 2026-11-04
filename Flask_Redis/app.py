import os
import socket

from flask import Flask
import redis

app = Flask(__name__)

redis_host = os.getenv("REDIS_HOST", "redis")
redis_port = int(os.getenv("REDIS_PORT", "6379"))

r = redis.Redis(host=redis_host, port=redis_port)

hostname = socket.gethostname()


@app.route("/")
def welcome():
    return f"Welcome to the CoderCo Containers Challenge! Served by {hostname}\n"


@app.route("/count")
def count():
    visits = r.incr("visits")
    return f"This page has been visited {visits} times. Served by {hostname}\n"


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
