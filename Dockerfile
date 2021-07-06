FROM sudobmitch/base:scratch as base-scratch
FROM buildpack-deps:focal as base


# ---------------------------
# Install OS packages
# necessary to build the
# other stages.
# ---------------------------

RUN set -x \
    # && echo deb http://archive.ubuntu.com/ubuntu universe multiverse >> /etc/apt/sources.list \
    && apt-get update \
    && apt-get install --no-install-recommends -y \
    # ... for princexml:
    gdebi fonts-stix libcurl4 \
    # ... for bakery-scripts
    build-essential libicu-dev pkg-config libmagic1 \
    mime-support wget curl xsltproc lsb-release git \
    imagemagick icc-profiles-free curl unzip \
    # ... for neb:
    python3 python3-pip python3-venv build-essential wget openjdk-11-jre-headless libmagic1 mime-support \
    # ... for mathify:
    libpangocairo-1.0-0 libxcomposite1 libxcursor1 libxdamage1 libxi6 libxext6 libcups2 libxrandr2 \
    libatk1.0-0 libgtk-3-0 libx11-xcb1 libnss3 libxss1 libasound2 \
    libxcb-dri3-0 libdrm2 libgbm1 \
    # ... for cnx-easybake:
    build-essential libicu-dev pkg-config python3-dev \
    ;


# ---------------------------
# Install princexml
# ---------------------------

ENV PRINCE_VERSION=12.5.1-1
ENV PRINCE_UBUNTU_BUILD=20.04

RUN wget --directory-prefix=/tmp/ https://www.princexml.com/download/prince_${PRINCE_VERSION}_ubuntu${PRINCE_UBUNTU_BUILD}_amd64.deb

RUN gdebi --non-interactive /tmp/prince_${PRINCE_VERSION}_ubuntu${PRINCE_UBUNTU_BUILD}_amd64.deb

# ---------------------------
# Install jq and Pandoc
# ---------------------------
ENV JQ_VERSION='1.6'
ENV PANDOC_VERSION='2.11.3.2'

RUN wget --no-check-certificate https://raw.githubusercontent.com/stedolan/jq/master/sig/jq-release.key -O /tmp/jq-release.key && \
    wget --no-check-certificate https://raw.githubusercontent.com/stedolan/jq/master/sig/v${JQ_VERSION}/jq-linux64.asc -O /tmp/jq-linux64.asc && \
    wget --no-check-certificate https://github.com/stedolan/jq/releases/download/jq-${JQ_VERSION}/jq-linux64 -O /tmp/jq-linux64 && \
    gpg --import /tmp/jq-release.key && \
    gpg --verify /tmp/jq-linux64.asc /tmp/jq-linux64 && \
    cp /tmp/jq-linux64 /usr/bin/jq && \
    chmod +x /usr/bin/jq && \
    rm -f /tmp/jq-release.key && \
    rm -f /tmp/jq-linux64.asc && \
    rm -f /tmp/jq-linux64

RUN wget https://github.com/jgm/pandoc/releases/download/${PANDOC_VERSION}/pandoc-${PANDOC_VERSION}-1-amd64.deb -O /tmp/pandoc.deb && \
    dpkg -i /tmp/pandoc.deb && \
    rm -f /tmp/pandoc.deb


# Remove unnecessary apt and temp files
RUN apt-get autoremove -y \
    && rm -rf /var/lib/apt/lists/* /tmp/* /var/tmp/*


# ---------------------------
# Install ruby
# ---------------------------

ENV RUBY_VERSION=2.6.6

RUN curl -fsSL https://rvm.io/mpapis.asc | gpg --import - \
    && curl -fsSL https://rvm.io/pkuczynski.asc | gpg --import - \
    && curl -fsSL https://get.rvm.io | bash -s stable \
    && bash -lc " \
        rvm requirements \
        && rvm install ${RUBY_VERSION} \
        && rvm use ${RUBY_VERSION} --default \
        && rvm rubygems current \
        && gem install bundler --no-document" # \
    # && echo '[[ -s "$HOME/.rvm/scripts/rvm" ]] && source "$HOME/.rvm/scripts/rvm" # Load RVM into a shell session *as a function*' >> /home/gitpod/.bashrc.d/70-ruby
RUN echo "rvm_gems_path=/workspace/.rvm" > ~/.rvmrc
ENV PATH=$PATH:/usr/local/rvm/rubies/ruby-${RUBY_VERSION}/bin/
ENV GEM_HOME=/usr/local/rvm/gems/ruby-${RUBY_VERSION}
ENV GEM_PATH=/usr/local/rvm/gems/ruby-${RUBY_VERSION}:/usr/local/rvm/gems/ruby-${RUBY_VERSION}@global


# ---------------------------
# Install node
# ---------------------------

# Source: https://github.com/gitpod-io/workspace-images/blob/master/full/Dockerfile#L139
ENV NODE_VERSION=14.16.1
RUN curl -fsSL https://raw.githubusercontent.com/nvm-sh/nvm/v0.37.2/install.sh | PROFILE=/dev/null bash \
    && bash -c ". $HOME/.nvm/nvm.sh \
        && nvm install $NODE_VERSION \
        && nvm alias default $NODE_VERSION \
        && npm install -g typescript yarn node-gyp"
    # && echo ". ~/.nvm/nvm-lazy.sh"  >> /home/gitpod/.bashrc.d/50-node

ENV PATH=$PATH:/root/.nvm/versions/node/v$NODE_VERSION/bin/


# -----------------------
# Create Virtualenv
# -----------------------

RUN python3 -m venv /openstax/venv && \
  . /openstax/venv/bin/activate && \
  pip3 install --no-cache-dir -U 'pip<20'


# ---------------------------
# Install mathify
# ---------------------------

FROM base as build-mathify-stage

COPY ./mathify/package.json ./mathify/package-lock.json /openstax/mathify/
WORKDIR /openstax/mathify/
RUN npm ci
COPY ./mathify/typeset /openstax/mathify/typeset


# ===========================
# Install Python Packages
# ===========================


FROM base AS build-python-stage

# ---------------------------
# Install cnx-easybake
# ---------------------------

COPY ./cnx-easybake/requirements/main.txt /openstax/cnx-easybake/requirements/
WORKDIR /openstax/cnx-easybake/
RUN . /openstax/venv/bin/activate && python3 -m pip install -r requirements/main.txt

COPY ./cnx-easybake/ /openstax/cnx-easybake/
RUN . /openstax/venv/bin/activate && python3 -m pip install "."


# ---------------------------
# Install neb
# ---------------------------

COPY ./nebuchadnezzar/requirements /openstax/nebuchadnezzar/requirements
WORKDIR /openstax/nebuchadnezzar/
# Install Python Dependencies
RUN set -x \
    && . /openstax/venv/bin/activate \
    && pip3 install -U setuptools wheel \
    && pip3 install -r ./requirements/main.txt

COPY ./nebuchadnezzar/ /openstax/nebuchadnezzar/

# Install neb
RUN . /openstax/venv/bin/activate \
    && pip3 install .


# -----------------------
# Install bakery-scripts
# -----------------------

ENV BAKERY_SCRIPTS_ROOT=./output-producer-service/bakery/src/scripts

COPY ${BAKERY_SCRIPTS_ROOT}/requirements.txt /openstax/bakery-scripts/scripts/
WORKDIR /openstax/bakery-scripts/

RUN . /openstax/venv/bin/activate && pip3 install -r scripts/requirements.txt

COPY ${BAKERY_SCRIPTS_ROOT}/*.py ${BAKERY_SCRIPTS_ROOT}/*.js ${BAKERY_SCRIPTS_ROOT}/*.json /openstax/bakery-scripts/scripts/
COPY ${BAKERY_SCRIPTS_ROOT}/gdoc/ /openstax/bakery-scripts/gdoc/

RUN . /openstax/venv/bin/activate && pip3 install /openstax/bakery-scripts/scripts/.
RUN npm --prefix /openstax/bakery-scripts/scripts install --production /openstax/bakery-scripts/scripts

# TODO: Move this into bakery-scripts/scripts/package.json
RUN npm --prefix /openstax/bakery-scripts/scripts install pm2@4.5.0


# ---------------------------
# Install xhtml-validator jar
# ---------------------------
FROM base AS build-xhtml-validator-stage
COPY ./xhtml-validator/ /openstax/xhtml-validator/
WORKDIR /openstax/xhtml-validator

RUN ./gradlew jar
# FROM validator/validator:20.3.16


# ---------------------------
# Install kcov
FROM base AS build-kcov-stage

RUN git clone https://github.com/SimonKagstrom/kcov /kcov-src/

RUN apt-get install -y \
        binutils-dev \
        build-essential \
        cmake \
        git \
        libcurl4-openssl-dev \
        libdw-dev \
        libiberty-dev \
        libssl-dev \
        ninja-build \
        python3 \
        zlib1g-dev \
        ;

RUN mkdir /kcov-src/build && \
    cd /kcov-src/build && \
    cmake -G 'Ninja' .. && \
    cmake --build . && \
    cmake --build . --target install


# ===========================
# The Final Stage
# ===========================
FROM base as runner

# ---------------------------
# Install dependencies that
# are not needed to prepare
# the other steps but are
# necessary to run the code.
# ---------------------------
RUN set -x \
    ### Git ###
    add-apt-repository -y ppa:git-core/ppa \
    && apt-get update \
    && apt-get install --no-install-recommends -y \
        git \
        libdw-dev \
        libxtst6 \
        # ... for parsing XML files: https://github.com/openstax/content-synchronizer/pull/7
        xmlstarlet \
        ;

# ---------------------------
# Install Adobe color mapping files
# ---------------------------
RUN curl -o /tmp/AdobeICCProfiles.zip https://download.adobe.com/pub/adobe/iccprofiles/win/AdobeICCProfilesCS4Win_end-user.zip \
    && unzip -o -j "/tmp/AdobeICCProfiles.zip" "Adobe ICC Profiles (end-user)/CMYK/USWebCoatedSWOP.icc" -d /usr/share/color/icc/ \
    && rm -f /tmp/AdobeICCProfiles.zip \
    ;


# ---------------------------
# Install recipes
# ---------------------------

COPY ./recipes/ /openstax/recipes/
WORKDIR /openstax/recipes/

RUN gem install bundler --no-document && \
    gem install byebug --no-document && \
    bundle config set no-cache 'true' && \
    bundle config set silence_root_warning 'true'

RUN ./scripts/install_used_gem_versions


# ---------------------------
# Install the Concourse Resource
# ---------------------------

COPY ./output-producer-resource /openstax/output-producer-resource/

WORKDIR /openstax/output-producer-resource/

RUN set -x \
    && . /openstax/venv/bin/activate \
    && python3 setup.py sdist \
    && pip3 install dist/output-producer-resource-*.tar.gz

RUN mkdir -p /opt/resource
RUN set -x \
    && . /openstax/venv/bin/activate \
    && for script in check in out; do ln -s $(which $script) /opt/resource/; done


WORKDIR /data/

RUN useradd --create-home -u 5000 app
RUN mv /root/.nvm /openstax/nvm
ENV PATH=$PATH:/openstax/nvm/versions/node/v$NODE_VERSION/bin/

COPY --from=base-scratch / /

# ---------------------------
# Copy the stages over
# ---------------------------
COPY --from=build-kcov-stage /usr/local/bin/kcov* /usr/local/bin/
COPY --from=build-kcov-stage /usr/local/share/doc/kcov /usr/local/share/doc/kcov

COPY --from=build-xhtml-validator-stage /openstax/xhtml-validator/build/libs/xhtml-validator.jar /openstax/xhtml-validator/
COPY --from=build-mathify-stage /openstax/mathify/ /openstax/mathify/
COPY --from=build-python-stage /openstax/bakery-scripts/scripts /openstax/bakery-scripts/scripts
COPY --from=build-python-stage /openstax/bakery-scripts/gdoc /openstax/bakery-scripts/gdoc
COPY --from=build-python-stage /openstax/venv/ /openstax/venv/

# Copy cnx-recipes styles
COPY ./cnx-recipes/recipes/output/ /openstax/cnx-recipes-recipes-output/
COPY ./cnx-recipes/styles/output/ /openstax/cnx-recipes-styles-output/


ENV PATH=$PATH:/dockerfiles/
COPY ./dockerfiles/10-fix-perms.sh /etc/entrypoint.d/
COPY ./dockerfiles/entrypointd.sh \
    ./dockerfiles/docker-entrypoint.sh \
    ./dockerfiles/docker-entrypoint-with-kcov.sh \
    /dockerfiles/


ENV RUN_AS="app:app"
ENV ORIG_ENTRYPOINT='/dockerfiles/docker-entrypoint-with-kcov.sh'
ENTRYPOINT ["/dockerfiles/entrypointd.sh"]
HEALTHCHECK CMD /dockerfiles/healthcheckd.sh
