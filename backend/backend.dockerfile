FROM python:3.7

LABEL maintainer="OpenStax Content Engineering"

RUN pip install fastapi uvicorn gunicorn jinja2 psycopg2-binary alembic SQLAlchemy tenacity

COPY ./docker/start.sh /start.sh
RUN chmod +x /start.sh

COPY ./docker/gunicorn.conf /gunicorn.conf

# For development, Jupyter remote kernel, Hydrogen
# Using inside the container:
# jupyter lab --ip=0.0.0.0 --allow-root --NotebookApp.custom_display_url=http://127.0.0.1:8888
ARG env=prod
RUN bash -c "if [ $env == 'dev' ] ; then pip install jupyterlab ; fi"
EXPOSE 8888

COPY ./app /app
WORKDIR /app/

ENV PYTHONPATH=/app

EXPOSE 80

CMD ["/start.sh"]
