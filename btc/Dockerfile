FROM debian:stable-slim AS builde

ARG USER_ID=1000
ARG GROUP_ID=1000

ENV BITCOIN_VERSION=30.0 \
    BITCOIN_ROOT=/opt/bitcoind \
    BITCOIN_BIN=/opt/bitcoind/bin \
    BITCOIN_DATA=/opt/bitcoind/data \
    PATH=/opt/bitcoind/bin:$PATH

RUN apt-get update && apt-get install -y wget tar ca-certificates \
    && rm -rf /var/lib/apt/lists/*

RUN groupadd -g ${GROUP_ID} bitcoin && \
    useradd -u ${USER_ID} -g bitcoin -s /bin/bash -m bitcoin

RUN mkdir -p ${BITCOIN_BIN} ${BITCOIN_DATA} \
    && chown -R bitcoin:bitcoin ${BITCOIN_ROOT}

COPY bitcoin.conf ${BITCOIN_ROOT}/bitcoin.conf

RUN cd /opt \
 && wget https://bitcoincore.org/bin/bitcoin-core-${BITCOIN_VERSION}/bitcoin-${BITCOIN_VERSION}-x86_64-linux-gnu.tar.gz \
 && tar -xzf bitcoin-${BITCOIN_VERSION}-x86_64-linux-gnu.tar.gz -C /opt \
 && mv /opt/bitcoin-${BITCOIN_VERSION}/bin/* ${BITCOIN_BIN}/ \
 && rm -rf /opt/bitcoin-${BITCOIN_VERSION} /opt/bitcoin-${BITCOIN_VERSION}-x86_64-linux-gnu.tar.gz

EXPOSE 8332 8333 18332 18333 
# 18443 18444 Uncomment for regtest

VOLUME ["${BITCOIN_DATA}"]

USER bitcoin

WORKDIR ${BITCOIN_ROOT}

ENTRYPOINT ["bitcoind"]
CMD ["-printtoconsole", "-conf=${BITCOIN_ROOT}/bitcoin.conf"]