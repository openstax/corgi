FROM python:3.7

LABEL maintainer="OpenStax Content Engineering"

RUN curl https://raw.githubusercontent.com/vishnubob/wait-for-it/54d1f0bfeb6557adf8a3204455389d0901652242/wait-for-it.sh \
  -o /usr/local/bin/wait-for-it && chmod a+x /usr/local/bin/wait-for-it

COPY ./docker/start.sh /start.sh
RUN chmod +x /start.sh

COPY ./docker/gunicorn.conf /gunicorn.conf

COPY ./app /app
WORKDIR /app/

ENV PYTHONPATH=/app

# For development, Jupyter remote kernel, Hydrogen
# Using inside the container:
# jupyter lab --ip=0.0.0.0 --allow-root --NotebookApp.custom_display_url=http://127.0.0.1:8888
ARG env=prod
RUN bash -c "if [ $env == 'dev' ] ; then make install_dev_requirements ; fi"
EXPOSE 8888

RUN make install_main_requirements

EXPOSE 80

CMD ["/start.sh"]
