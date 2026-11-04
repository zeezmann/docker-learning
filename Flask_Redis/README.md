# Flask + Redis Visit Counter

My solution to the CoderCo Containers Challenge. A Flask web app that counts visits in Redis, run as a multi-container app with Docker Compose.

It covers the core challenge and all three bonuses: persistent storage, environment variables, and scaling with a load balancer.

## How it works

```
            localhost:5000
                  |
          nginx (port 80 inside)
          /       |       \
       web-1    web-2    web-3     Flask, port 5000
          \       |       /
             redis (6379)
                  |
          redis-data volume
```

- **nginx** is the only service published to the host. It takes every request on port 5000 and round-robins it across the Flask containers.
- **web** runs 3 replicas of the Flask app. None of them publish a port. They're only reachable through nginx.
- **redis** stores the visit count. It isn't published to the host either, since only the Flask containers need to reach it over the Compose network.
- **redis-data** is a named volume, so the count survives the containers being removed and recreated.

## Routes

| Route | What it does |
|---|---|
| `/` | Welcome message, plus the ID of the container that served it |
| `/count` | Increments the visit count in Redis and returns it, plus the container ID |

## Running it

From this folder:

```
docker compose up -d --build
```

Test it:

```
curl http://localhost:5000/
curl http://localhost:5000/count
```

To see the load balancing, send a few requests in a row:

```
for i in $(seq 1 6)
do
  curl -s http://localhost:5000/count
done
```

The count goes up by one each time, and the container ID rotates through three different values.

To stop it, keeping the count:

```
docker compose down
```

`docker compose down -v` also deletes the volume and resets the count.

## Design decisions

- **Redis `INCR` for the counter.** It's atomic, so three Flask containers hitting Redis at the same time can't lose counts the way a read, add one, write back approach would.
- **Named volume for Redis.** The Redis image gives each container an anonymous volume. When I tested `compose down` then `up` without a named volume, the new container got a fresh empty volume and the count reset to 1. The old data was still on disk, just orphaned.
- **No port on the web service.** Scaling to 3 with `"5000:5000"` failed straight away, because only one container can bind host port 5000. Moving the published port to nginx fixed it.
- **Replicas set in the Compose file**, not with `--scale` on the command line, so the intended setup lives in Git and every `up` gives the same result.
- **nginx config baked into its own image** rather than bind-mounted, so the image is self-contained and would run anywhere it's pulled.
- **`init: true` on the Flask service.** Without it, Python runs as PID 1 and ignores `SIGTERM`, so `docker compose stop` took 10 seconds and force-killed it (exit 137). With it, it stops in under a second (exit 143).
- **Dependencies installed before the app code is copied**, so changing `app.py` doesn't re-run `pip install`.
- **Pinned versions** for the base images and Python libraries, so a rebuild next month gives the same result.

## What I'd improve next

- Pin the full dependency tree with a lock file. I pinned Flask, but Werkzeug, which Flask depends on, still floats.
- Add health checks so `depends_on` waits for Redis to actually be ready, not just started.
- nginx only looks up the web containers when it starts, so changing the replica count needs an nginx restart. A production load balancer would re-resolve regularly.
- Set a password on Redis. It's only reachable inside the Compose network here, but it shouldn't rely on that alone.
