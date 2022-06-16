FROM openstax/ubuntu-20.04:latest

# copy files
COPY ./app/pyproject.toml /build/pyproject.toml
COPY ./app/poetry.lock /build/poetry.lock

# change working directory
WORKDIR /build

ENV PLAYWRIGHT_BROWSERS_PATH=/ms-playwright

# Create Virtualenv
RUN python3 -m venv /opt/venv && \
  . /opt/venv/bin/activate && \
  pip install --no-cache-dir -U 'pip' && \
  poetry install --no-root --no-interaction && \
  playwright install chromium --with-deps

RUN curl https://raw.githubusercontent.com/vishnubob/wait-for-it/54d1f0bfeb6557adf8a3204455389d0901652242/wait-for-it.sh \
  -o /usr/local/bin/wait-for-it && chmod a+x /usr/local/bin/wait-for-it

WORKDIR /app/

COPY ./app /app

# make sure we use the virtualenv
ENV PATH="/opt/venv/bin:$PATH"

# add our app to the path
ENV PYTHONPATH="/app:$PYTHONPATH"
