FROM docker:29-cli AS dockercli

FROM jenkins/jenkins:lts-jdk21

USER root

RUN apt-get update && apt-get install -y --no-install-recommends \
    git \
    python3 \
    python3-venv \
    python3-pip \
    curl \
    ca-certificates \
    && rm -rf /var/lib/apt/lists/*

COPY --from=dockercli /usr/local/bin/docker /usr/local/bin/docker
COPY --from=dockercli /usr/local/libexec/docker/cli-plugins/docker-compose /usr/local/lib/docker/cli-plugins/docker-compose

RUN chmod +x /usr/local/bin/docker /usr/local/lib/docker/cli-plugins/docker-compose

ENV DOCKER_CONFIG=/var/jenkins_home/.docker

USER root
