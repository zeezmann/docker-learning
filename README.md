# Docker Learning

Hands-on Docker work from the CoderCo DevOps roadmap. Each folder is a separate project with its own Dockerfile and Compose setup.

## Projects

### [Flask_App](./Flask_App)
A Flask app connected to MySQL, run with Docker Compose.

- Containerised the app and ran it alongside a MySQL container, with Flask reaching the database by its Compose service name
- Pushed the image to Docker Hub and Amazon ECR (eu-west-2), then pulled and ran it from both
- Worked through cross-architecture issues on Apple Silicon, running amd64 images with `--platform linux/amd64`
- Built a multi-stage version of the image, which cut the content size from 156 MB to 88 MB while keeping the build tools out of the final image
- Tracked down a stale image in ECR that had old code baked in, rebuilt it from source and tagged it with the commit hash so it's clear what's inside

### [Flask_Redis](./Flask_Redis)
My solution to the CoderCo Containers Challenge. A Flask visit counter backed by Redis, running as 3 replicas behind an nginx load balancer, with persistent storage. See the project README for the full write-up.

## What I've covered

- Images, containers and Dockerfiles
- Layer caching and ordering Dockerfile steps so rebuilds stay fast
- Docker Compose for multi-container apps
- Container networking and Docker's built-in DNS
- Named volumes versus anonymous volumes
- Environment variables for configuration
- Registries: Docker Hub and Amazon ECR
- Multi-stage builds and image size
- Load balancing with nginx as a reverse proxy
- Troubleshooting with logs, exit codes and inspecting what's actually inside an image

## Running a project

Each project runs from its own folder:

```
cd Flask_Redis
docker compose up -d --build
```

Note: Flask_App's Compose file pulls the web image from my private ECR repository, so it needs AWS access to run as is. Change `image:` back to `build: .` to build it locally instead.
