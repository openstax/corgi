FROM sphinxdoc/sphinx:7.1.2 as base

COPY requirements.txt /docs/requirements.txt
RUN pip install -r /docs/requirements.txt


FROM base as runner

COPY . /docs
EXPOSE 8000
CMD sphinx-autobuild --host 0.0.0.0 --port 8000 /docs /build/html
