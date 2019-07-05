FROM phusion/baseimage:0.9.19
MAINTAINER Total Games LLC and contributors

ARG PLAYCHAIN_SRC_DIR

ARG USER=witness
ARG PLAYCHAIN_HOME=/var/lib/playchain
ARG LIVE_TESTNET

ARG CONFIG_OFF_LOGO
ARG CONFIG_DEBUG
ARG CONFIG_EXTERNAL_PLAYCHAIN_DATABASE_API_URL
ARG CONFIG_EXTERNAL_PLAYCHAIN_DATABASE_P2P_URL
ARG CONFIG_PLAYCHAIN_DATABASE_API_INTERFACE=0.0.0.0
ARG CONFIG_PLAYCHAIN_DATABASE_API_PORT=8500
ARG CONFIG_PLAYCHAIN_DATABASE_P2P_INTERFACE=0.0.0.0
ARG CONFIG_PLAYCHAIN_DATABASE_P2P_PORT=10300
ARG CONFIG_GENESIS

ENV USER=${USER}
ENV LIVE_TESTNET=${LIVE_TESTNET:-OFF}
ENV CONFIG_OFF_LOGO=${CONFIG_OFF_LOGO}
ENV CONFIG_DEBUG=${CONFIG_DEBUG}
ENV CONFIG_EXTERNAL_PLAYCHAIN_DATABASE_API_URL=${CONFIG_EXTERNAL_PLAYCHAIN_DATABASE_API_URL}
ENV CONFIG_EXTERNAL_PLAYCHAIN_DATABASE_P2P_URL=${CONFIG_EXTERNAL_PLAYCHAIN_DATABASE_P2P_URL}
ENV CONFIG_PLAYCHAIN_DATABASE_API_INTERFACE=${CONFIG_PLAYCHAIN_DATABASE_API_INTERFACE}
ENV CONFIG_PLAYCHAIN_DATABASE_API_PORT=${CONFIG_PLAYCHAIN_DATABASE_API_PORT}
ENV CONFIG_PLAYCHAIN_DATABASE_P2P_INTERFACE=${CONFIG_PLAYCHAIN_DATABASE_P2P_INTERFACE}
ENV CONFIG_PLAYCHAIN_DATABASE_P2P_PORT=${CONFIG_PLAYCHAIN_DATABASE_P2P_PORT}
ENV CONFIG_GENESIS=${CONFIG_GENESIS}

ENV LANG=en_US.UTF-8
RUN \
    apt-get update -y && \
    apt-get install -y \
      g++ \
      autoconf \
      cmake \
      git \
      libbz2-dev \
      libreadline-dev \
      libboost-all-dev \
      libssl-dev \
      libncurses-dev \
      doxygen \
      libcurl4-openssl-dev \
      python3 \
      python3-pip \
    && \
    apt-get update -y && \
    apt-get install -y fish && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/* /tmp/* /var/tmp/*

# Install Python additional libraries
RUN pip3 install click && \
    pip3 install colorama && \
    pip3 install requests

ADD ${PLAYCHAIN_SRC_DIR} /playchain/src
WORKDIR /playchain/src
RUN \
    mkdir build && \
    cd build && \
    cmake \
        -DCMAKE_BUILD_TYPE=Release \
        -DGENESIS_TESTNET=${LIVE_TESTNET} \
        -DUTESTS_DISABLE_ALL_TESTS=ON \
        .. && \
    make -j$(nproc) && \
    make install && \
    #
    # Obtain version
    mkdir -p /etc/playchain && \
    git rev-parse --short HEAD > /etc/playchain/version && \
    cd / && \
    rm -rf /playchain/src

# Home directory $HOME
WORKDIR /
RUN useradd -s /bin/bash -m -d ${PLAYCHAIN_HOME} ${USER}
ENV HOME ${PLAYCHAIN_HOME}
RUN chown ${USER}:${USER} -R ${PLAYCHAIN_HOME}

# Volume
VOLUME ["/var/lib/playchain", "/etc/playchain"]

EXPOSE ${CONFIG_PLAYCHAIN_DATABASE_API_PORT}
EXPOSE ${CONFIG_PLAYCHAIN_DATABASE_P2P_PORT}

# default exec/config files
ADD docker/playchain.config.template.ini /etc/playchain/playchain.config.template.ini

RUN \
    chmod 644 /etc/playchain/playchain.config.template.ini

ADD docker/witnessentry.sh /usr/local/bin/witnessentry.sh
ADD docker/witnessentry.py /usr/local/bin/witnessentry.py
RUN \
    chmod a+x /usr/local/bin/witnessentry.sh && \
    chmod a+x /usr/local/bin/witnessentry.py

# default execute entry
CMD ["/bin/bash", "/usr/local/bin/witnessentry.sh"]
