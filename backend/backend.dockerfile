FROM openstax/python3-base:latest as base

RUN apt-get update -qq \
 && apt-get install -y --no-install-recommends \
    # required by psycopg2 at build and runtime
    libpq-dev \
 && apt-get autoremove -y

FROM openstax/python3-poetry:latest as dev-builder

# Only include pyproject and poetry.lock in cache invalidation
COPY ./app/pyproject.toml ./app/poetry.lock /build/

# change working directory
WORKDIR /build

# Create Virtualenv
RUN python -m venv /opt/venv && \
  . /opt/venv/bin/activate && \
  pip install --no-cache-dir -U 'pip' && \
  poetry install --no-root --no-interaction

FROM openstax/python3-poetry:latest as prod-builder

# copy files
COPY ./app /build/

# change working directory
WORKDIR /build

# Create Virtualenv
RUN python -m venv /opt/venv && \
  . /opt/venv/bin/activate && \
  pip install --no-cache-dir -U 'pip' && \
  poetry install --without dev --no-root --no-interaction

FROM base as dev-runner

# install wait-for-it
# allows us to wait for specific services to be up before executing scripts
RUN curl https://raw.githubusercontent.com/vishnubob/wait-for-it/54d1f0bfeb6557adf8a3204455389d0901652242/wait-for-it.sh \
  -o /usr/local/bin/wait-for-it && chmod a+x /usr/local/bin/wait-for-it

# copy everything from /opt
COPY --from=dev-builder /opt/venv /opt/venv

# make sure we use the virtualenv
ENV PATH="/opt/venv/bin:$PATH"

# add our app to the path
ENV PYTHONPATH="/app:$PYTHONPATH"

COPY ./docker/start.sh /start.sh
RUN chmod +x /start.sh

COPY ./docker/gunicorn.conf /gunicorn.conf

COPY ./app /app
WORKDIR /app

EXPOSE 3000
EXPOSE 8888
EXPOSE 80

CMD ["/start.sh"]

FROM base as prod-runner

# install wait-for-it
# allows us to wait for specific services to be up before executing scripts
RUN curl https://raw.githubusercontent.com/vishnubob/wait-for-it/54d1f0bfeb6557adf8a3204455389d0901652242/wait-for-it.sh \
  -o /usr/local/bin/wait-for-it && chmod a+x /usr/local/bin/wait-for-it

# copy everything from /opt
COPY --from=prod-builder /opt/venv /opt/venv

# make sure we use the virtualenv
ENV PATH="/opt/venv/bin:$PATH"

# add our app to the path
ENV PYTHONPATH="/app:$PYTHONPATH"

COPY ./docker/start.sh /start.sh
RUN chmod +x /start.sh

COPY ./docker/gunicorn.conf /gunicorn.conf

COPY ./app /app
WORKDIR /app

EXPOSE 8888
EXPOSE 80

CMD ["/start.sh"]
