FROM openstax/selenium-chrome-debug:latest as base

# We have a poetry image available but it uses python 3.8 which causes issues
# The qa selenium base image uses python 3.7 so we need to build specifically
# for that version. When the selenium image is updated to 3.8+ we can update this.
FROM openstax/python3-poetry:latest as builder

# copy files
COPY ./app /build/

# change working directory
WORKDIR /build

# Create Virtualenv
RUN python -m venv /opt/venv && \
  . /opt/venv/bin/activate && \
  pip install --no-cache-dir -U 'pip' && \
  poetry install --no-root --no-interaction

FROM base as runner

USER root

RUN curl https://raw.githubusercontent.com/vishnubob/wait-for-it/54d1f0bfeb6557adf8a3204455389d0901652242/wait-for-it.sh \
  -o /usr/local/bin/wait-for-it && chmod a+x /usr/local/bin/wait-for-it

COPY --from=builder /opt/venv /opt/venv
COPY --chown=seluser ./app /app
WORKDIR /app/

# make sure we use the virtualenv
ENV PATH="/opt/venv/bin:$PATH"

# add our app to the path
ENV PYTHONPATH="/app:$PYTHONPATH"

USER seluser
