# <>=======()                             
#(/\___   /|\          ()==========<>_   
#      \_/ | \        //|\   ______/ \)  
#        \_|  \      // | \_/            
#          \|\/|\_   //  /\/              
#           (oo)\ \_//  /                 
#          //_/\_\/ /  |                  
#         @@/  |=\  \  |                  
#              \_=\_ \ |                  
#                \==\ \|\_ snd            
#             __(\===\(  )\               
#            (((~) __(_/   |              
#                 (((~) \  /              
#                 ______/ /               
#                 "------"                
#                                         
# ====================================================
# This file is autogenerated. Do not edit it directly.
# Run ./build-dockerfile.sh instead.
# ====================================================

# vvvvvvvvvvvvvvv Dockerfile.common vvvvvvvvvvvvvvv
FROM sudobmitch/base:scratch as base-scratch
FROM buildpack-deps:focal as base


# ---------------------------
# Install OS packages
# necessary to build the
# other stages.
# ---------------------------

RUN set -x \
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
    # ---------------------------
    # Dependencies that are not needed to prepare
    # the other steps but are necessary to run the code.
    # ---------------------------
    libdw-dev \
    libxtst6 \
    # ... for parsing XML files: https://github.com/openstax/content-synchronizer/pull/7
    xmlstarlet \
    # For debugging
    vim \
    nano \
    ;

# ---------------------------
# Install Adobe color mapping files
# ---------------------------
RUN curl -o /tmp/AdobeICCProfiles.zip https://download.adobe.com/pub/adobe/iccprofiles/win/AdobeICCProfilesCS4Win_end-user.zip \
    && unzip -o -j "/tmp/AdobeICCProfiles.zip" "Adobe ICC Profiles (end-user)/CMYK/USWebCoatedSWOP.icc" -d /usr/share/color/icc/ \
    && rm -f /tmp/AdobeICCProfiles.zip \
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

RUN wget --no-check-certificate https://raw.githubusercontent.com/stedolan/jq/master/sig/jq-release.key -O /tmp/jq-release.key \
    && wget --no-check-certificate https://raw.githubusercontent.com/stedolan/jq/master/sig/v${JQ_VERSION}/jq-linux64.asc -O /tmp/jq-linux64.asc \
    && wget --no-check-certificate https://github.com/stedolan/jq/releases/download/jq-${JQ_VERSION}/jq-linux64 -O /tmp/jq-linux64 \
    && gpg --import /tmp/jq-release.key \
    && gpg --verify /tmp/jq-linux64.asc /tmp/jq-linux64 \
    && cp /tmp/jq-linux64 /usr/bin/jq \
    && chmod +x /usr/bin/jq \
    && rm -f /tmp/jq-release.key \
    && rm -f /tmp/jq-linux64.asc \
    && rm -f /tmp/jq-linux64 \
    ;

RUN wget https://github.com/jgm/pandoc/releases/download/${PANDOC_VERSION}/pandoc-${PANDOC_VERSION}-1-amd64.deb -O /tmp/pandoc.deb \
    && dpkg -i /tmp/pandoc.deb \
    && rm -f /tmp/pandoc.deb \
    ;


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


# Use this so that gitpod directories are the same.
# TODO: Maybe this ENV should be set in a gitpod-specific Dockerfile (if that's possible)
ENV PROJECT_ROOT=/workspace/richb-press


# ---------------------------
# Install node
# ---------------------------

# Source: https://github.com/gitpod-io/workspace-images/blob/master/full/Dockerfile#L139
ENV NODE_VERSION=14.16.1

COPY                ./dockerfiles/build/build-system-node.env \
        $PROJECT_ROOT/dockerfiles/build/build-system-node.env
RUN .   $PROJECT_ROOT/dockerfiles/build/build-system-node.env

ENV PATH=$PATH:/root/.nvm/versions/node/v$NODE_VERSION/bin/


# -----------------------
# Create Virtualenv
# -----------------------

COPY            ./dockerfiles/build/build-system-venv.sh \
    $PROJECT_ROOT/dockerfiles/build/build-system-venv.sh
RUN $PROJECT_ROOT/dockerfiles/build/build-system-venv.sh


# ---------------------------
# Install mathify
# ---------------------------

FROM base as build-mathify-stage

COPY ./mathify/package.json ./mathify/package-lock.json $PROJECT_ROOT/mathify/

COPY            ./dockerfiles/build/build-stage-mathify.sh \
    $PROJECT_ROOT/dockerfiles/build/build-stage-mathify.sh
RUN $PROJECT_ROOT/dockerfiles/build/build-stage-mathify.sh

COPY ./mathify/typeset $PROJECT_ROOT/mathify/typeset

# ===========================
# Install Python Packages
# ===========================


FROM base AS build-python-stage

# ---------------------------
# Install cnx-easybake
# ---------------------------

COPY ./cnx-easybake/requirements/main.txt $PROJECT_ROOT/cnx-easybake/requirements/

COPY            ./dockerfiles/build/build-stage-easybake-3rdparty.bash \
    $PROJECT_ROOT/dockerfiles/build/build-stage-easybake-3rdparty.bash
RUN $PROJECT_ROOT/dockerfiles/build/build-stage-easybake-3rdparty.bash

COPY ./cnx-easybake/ $PROJECT_ROOT/cnx-easybake/

COPY            ./dockerfiles/build/build-stage-easybake-install.bash \
    $PROJECT_ROOT/dockerfiles/build/build-stage-easybake-install.bash
RUN $PROJECT_ROOT/dockerfiles/build/build-stage-easybake-install.bash


# ---------------------------
# Install neb
# ---------------------------

COPY ./nebuchadnezzar/requirements $PROJECT_ROOT/nebuchadnezzar/requirements

COPY            ./dockerfiles/build/build-stage-neb-3rdparty.bash \
    $PROJECT_ROOT/dockerfiles/build/build-stage-neb-3rdparty.bash
RUN $PROJECT_ROOT/dockerfiles/build/build-stage-neb-3rdparty.bash

COPY ./nebuchadnezzar/ $PROJECT_ROOT/nebuchadnezzar/

COPY            ./dockerfiles/build/build-stage-neb-install.bash \
    $PROJECT_ROOT/dockerfiles/build/build-stage-neb-install.bash
RUN $PROJECT_ROOT/dockerfiles/build/build-stage-neb-install.bash


# -----------------------
# Install bakery-scripts
# -----------------------

ENV HOST_BAKERY_SRC_ROOT=./output-producer-service/bakery/src
ENV BAKERY_SRC_ROOT=$PROJECT_ROOT/output-producer-service/bakery/src

COPY $HOST_BAKERY_SRC_ROOT/scripts/requirements.txt $BAKERY_SRC_ROOT/scripts/

COPY            ./dockerfiles/build/build-stage-bakery-3rdparty.bash \
    $PROJECT_ROOT/dockerfiles/build/build-stage-bakery-3rdparty.bash
RUN $PROJECT_ROOT/dockerfiles/build/build-stage-bakery-3rdparty.bash

COPY $HOST_BAKERY_SRC_ROOT/scripts/*.py $HOST_BAKERY_SRC_ROOT/scripts/*.js $HOST_BAKERY_SRC_ROOT/scripts/*.json $BAKERY_SRC_ROOT/scripts/
COPY $HOST_BAKERY_SRC_ROOT/scripts/gdoc/ $BAKERY_SRC_ROOT/scripts/gdoc/

COPY            ./dockerfiles/build/build-stage-bakery-install.bash \
    $PROJECT_ROOT/dockerfiles/build/build-stage-bakery-install.bash
RUN $PROJECT_ROOT/dockerfiles/build/build-stage-bakery-install.bash


# ---------------------------
# Install xhtml-validator jar
# ---------------------------
FROM base AS build-xhtml-validator-stage
COPY ./xhtml-validator/ $PROJECT_ROOT/xhtml-validator/

COPY            ./dockerfiles/build/build-stage-xhtmlvalidator.sh \
    $PROJECT_ROOT/dockerfiles/build/build-stage-xhtmlvalidator.sh
RUN $PROJECT_ROOT/dockerfiles/build/build-stage-xhtmlvalidator.sh


# ---------------------------
# Install kcov
FROM base AS build-kcov-stage

RUN git clone https://github.com/SimonKagstrom/kcov /kcov-src/

RUN apt-get update \
    && apt-get install -y \
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

RUN mkdir /kcov-src/build \
    && cd /kcov-src/build \
    && cmake -G 'Ninja' .. \
    && cmake --build . \
    && cmake --build . --target install \
    ;


# ===========================
# The Final Stage
# ===========================
FROM base as runner

# ---------------------------
# Install recipes
# ---------------------------

COPY ./recipes/ $PROJECT_ROOT/recipes/

COPY            ./dockerfiles/build/build-stage-recipes.sh \
    $PROJECT_ROOT/dockerfiles/build/build-stage-recipes.sh
RUN $PROJECT_ROOT/dockerfiles/build/build-stage-recipes.sh


# ---------------------------
# Install the Concourse Resource
# ---------------------------

COPY ./output-producer-resource $PROJECT_ROOT/output-producer-resource/

WORKDIR $PROJECT_ROOT/output-producer-resource/

RUN set -x \
    && . $PROJECT_ROOT/venv/bin/activate \
    && python3 setup.py sdist \
    && pip3 install dist/output-producer-resource-*.tar.gz

RUN mkdir -p /opt/resource
RUN set -x \
    && . $PROJECT_ROOT/venv/bin/activate \
    && for script in check in out; do ln -s $(which $script) /opt/resource/; done


RUN mv /root/.nvm $PROJECT_ROOT/nvm
ENV PATH=$PATH:$PROJECT_ROOT/nvm/versions/node/v$NODE_VERSION/bin/

COPY --from=base-scratch / /

# ---------------------------
# Copy the stages over
# ---------------------------

# This variable is JUST used for the COPY instructions below
ENV BAKERY_SRC_ROOT=$PROJECT_ROOT/output-producer-service/bakery/src

COPY --from=build-kcov-stage /usr/local/bin/kcov* /usr/local/bin/
COPY --from=build-kcov-stage /usr/local/share/doc/kcov /usr/local/share/doc/kcov

COPY --from=build-xhtml-validator-stage $PROJECT_ROOT/xhtml-validator/build/libs/xhtml-validator.jar $PROJECT_ROOT/xhtml-validator/build/libs/xhtml-validator.jar
COPY --from=build-mathify-stage $PROJECT_ROOT/mathify/ $PROJECT_ROOT/mathify/
COPY --from=build-python-stage $BAKERY_SRC_ROOT/scripts $BAKERY_SRC_ROOT/scripts
COPY --from=build-python-stage $BAKERY_SRC_ROOT/scripts/gdoc $BAKERY_SRC_ROOT/scripts/gdoc
COPY --from=build-python-stage $PROJECT_ROOT/venv/ $PROJECT_ROOT/venv/

# Copy cnx-recipes styles
COPY ./cnx-recipes/recipes/output/ $PROJECT_ROOT/cnx-recipes/recipes/output/
COPY ./cnx-recipes/styles/output/ $PROJECT_ROOT/cnx-recipes/styles/output/


ENV PATH=$PATH:/dockerfiles/
COPY ./dockerfiles/10-fix-perms.sh /etc/entrypoint.d/
COPY ./dockerfiles/steps /dockerfiles/steps
COPY ./dockerfiles/build /dockerfiles/build
COPY ./dockerfiles/entrypointd.sh \
    ./dockerfiles/docker-entrypoint.sh \
    ./dockerfiles/docker-entrypoint-with-kcov.sh \
    /dockerfiles/

COPY ./step-config.json $PROJECT_ROOT
# ^^^^^^^^^^^^^^^ Dockerfile.common ^^^^^^^^^^^^^^^

# vvvvvvvvvvv Dockerfile.cli-endmatter vvvvvvvvvvvv
WORKDIR /data/

RUN useradd --create-home -u 5000 app

ENV RUN_AS="app:app"
ENV ORIG_ENTRYPOINT='/dockerfiles/docker-entrypoint-with-kcov.sh'
ENTRYPOINT ["/dockerfiles/entrypointd.sh"]
HEALTHCHECK CMD /dockerfiles/healthcheckd.sh
