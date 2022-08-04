FROM openstax/ubuntu-20.04:latest

#=====
# VNC
#=====
RUN apt-get update -qqy \
  && apt-get -qqy install \
  x11vnc \
  && rm -rf /var/lib/apt/lists/* /var/cache/apt/*

#=========
# fluxbox
# A fast, lightweight and responsive window manager
#=========
RUN apt-get update -qqy \
  && apt-get -qqy install \
    fluxbox \
  && rm -rf /var/lib/apt/lists/* /var/cache/apt/*

#============================
# Some configuration options
#============================
ENV SCREEN_WIDTH 1360
ENV SCREEN_HEIGHT 1020
ENV SCREEN_DEPTH 24
ENV DISPLAY :99.0

#=======================================
# Add normal user with passwordless sudo
#=======================================
RUN useradd ceuser \
         --shell /bin/bash  \
         --create-home \
  && usermod -a -G sudo ceuser \
  && echo 'ALL ALL = (ALL) NOPASSWD: ALL' >> /etc/sudoers \
  && echo 'ceuser:secret' | chpasswd

#==============================
# Scripts to run Xvfb
#==============================
COPY ./docker/entry_point.sh \
    ./docker/functions.sh \
    /opt/bin/

#==============================
# Copy application requirements
#==============================
COPY ./app/pyproject.toml /build/pyproject.toml
COPY ./app/poetry.lock /build/poetry.lock

#==============================
# Install app requirements and playwright
#==============================
WORKDIR /build

ENV PLAYWRIGHT_BROWSERS_PATH=/ms-playwright

RUN python3 -m venv /opt/venv && \
  . /opt/venv/bin/activate && \
  pip install --no-cache-dir -U 'pip' && \
  poetry install --no-root --no-interaction && \
  playwright install chromium --with-deps

#==============================
# Install wait-for-it
#==============================
RUN curl https://raw.githubusercontent.com/vishnubob/wait-for-it/54d1f0bfeb6557adf8a3204455389d0901652242/wait-for-it.sh \
  -o /usr/local/bin/wait-for-it && chmod a+x /usr/local/bin/wait-for-it

WORKDIR /app/

COPY ./app /app

# make sure we use the virtualenv
ENV PATH="/opt/venv/bin:$PATH"

# add our app to the path
ENV PYTHONPATH="/app:$PYTHONPATH"

USER ceuser

RUN mkdir -p ~/.vnc \
  && x11vnc -storepasswd secret ~/.vnc/passwd \
  && sudo chown ceuser:ceuser ~/.vnc \
  && sudo chown ceuser:ceuser /opt/bin/entry_point.sh

EXPOSE 5900

ENTRYPOINT ["/opt/bin/entry_point.sh"]
