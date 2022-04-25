FROM openstax/python3-chrome-base:latest as base


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

ENV PLAYWRIGHT_BROWSERS_PATH=/ms-playwright

RUN mkdir /ms-playwright && \
    playwright install chromium --with-deps

FROM base as runner

RUN curl https://raw.githubusercontent.com/vishnubob/wait-for-it/54d1f0bfeb6557adf8a3204455389d0901652242/wait-for-it.sh \
  -o /usr/local/bin/wait-for-it && chmod a+x /usr/local/bin/wait-for-it

COPY --from=builder /opt/venv /opt/venv
COPY --from=builder /ms-playwright /ms-playwright
COPY ./app /app
WORKDIR /app/

# make sure we use the virtualenv
ENV PATH="/opt/venv/bin:$PATH"

# add our app to the path
ENV PYTHONPATH="/app:$PYTHONPATH"

ENV PLAYWRIGHT_BROWSERS_PATH=/ms-playwright
