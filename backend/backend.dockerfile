FROM openstax/python3-base:20211117.170559 as base

RUN apt-get update -qq \
 && apt-get install -y --no-install-recommends \
    # required by psycopg2 at build and runtime
    libpq-dev \
    curl \
 && apt-get autoremove -y

FROM openstax/python3-poetry:20211117.174217 as dev-builder

# copy files
COPY ./app /build/

# change working directory
WORKDIR /build

# Create Virtualenv
RUN python -m venv /opt/venv && \
  . /opt/venv/bin/activate && \
  pip install --no-cache-dir -U 'pip<20'

# Allow installing dev dependencies to run tests
ARG INSTALL_DEV=false
RUN bash -c "if [ $INSTALL_DEV == 'true' ] ; then . /opt/venv/bin/activate && poetry install --no-root --no-interaction; else . /opt/venv/bin/activate && poetry install --no-root --no-dev --no-interaction; fi"

# start a new build stage
FROM base as runner

# install wait-for-it
# allows us to wait for specific services to be up before executing scripts
RUN curl https://raw.githubusercontent.com/vishnubob/wait-for-it/54d1f0bfeb6557adf8a3204455389d0901652242/wait-for-it.sh \
  -o /usr/local/bin/wait-for-it && chmod a+x /usr/local/bin/wait-for-it

# copy everything from /opt
COPY --from=builder /opt/venv /opt/venv

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
