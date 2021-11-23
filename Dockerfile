FROM python:3.10.0-slim@sha256:3524d9553dd1ea815d9e3ff07a0ccafe878a9403fb5f9956dc6ad86075ac345f

ENV PYTHONUNBUFFERED=1 \
    PYTHONPATH=/app/ \
    PORT=8888

EXPOSE $PORT

# add a non-privileged user for installing and running
# the application
RUN mkdir /app && \
    chown 10001:10001 /app && \
    groupadd --gid 10001 app && \
    useradd --no-create-home --uid 10001 --gid 10001 --home-dir /app app

COPY requirements.txt .
COPY bin/docker-install.sh .
RUN ./docker-install.sh

# TODO: don't copy any /tests folders for prod image (maybe handle this in .dockerignore)
COPY . /app

# Switch back to home directory
WORKDIR /app

ENV PYTHONPATH "/app"

# Drop down to unprivileged user
RUN chown -R 10001:10001 /app

USER 10001


# Run uwsgi by default
ENTRYPOINT ["/bin/bash", "/app/bin/run.sh"]
CMD ["uwsgi", "--ini", "/etc/kinto.ini"]
