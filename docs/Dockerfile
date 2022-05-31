FROM openstax/python3-base:latest

LABEL maintainer="OpenStax Content Engineering"

COPY requirements.txt .

# Update System Dependencies
RUN set -x \
  && apt-get update && apt-get upgrade -y \
  && apt-get install make \
  && apt-get autoremove -y \
  && rm -rf /var/cache/* \
  && rm -rf /var/lib/apt/lists/*

RUN pip install -r requirements.txt

COPY . /docs

ENV DOC_DIR=/docs

WORKDIR $DOC_DIR

EXPOSE 8000

CMD make livehtml
