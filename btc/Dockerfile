FROM debian:stable-slim

ARG BITCOIN_VERSION=30.2
ARG TARGETARCH

ENV BITCOIN_VERSION=${BITCOIN_VERSION} \
    BITCOIN_ROOT=/opt/bitcoind \
    BITCOIN_BIN=/opt/bitcoind/bin \
    BITCOIN_DATA=/opt/bitcoind/data \
    PATH=/opt/bitcoind/bin:$PATH

RUN apt-get update && apt-get install -y wget tar ca-certificates \
    && rm -rf /var/lib/apt/lists/*

RUN mkdir -p ${BITCOIN_BIN} ${BITCOIN_DATA}

COPY bitcoin.conf ${BITCOIN_ROOT}/bitcoin.conf

# Download Bitcoin Core for the correct architecture
RUN ARCH=$(case ${TARGETARCH} in \
        "amd64") echo "x86_64-linux-gnu" ;; \
        "arm64") echo "aarch64-linux-gnu" ;; \
        *) echo "x86_64-linux-gnu" ;; \
    esac) && \
    cd /opt && \
    wget https://bitcoincore.org/bin/bitcoin-core-${BITCOIN_VERSION}/bitcoin-${BITCOIN_VERSION}-${ARCH}.tar.gz && \
    tar -xzf bitcoin-${BITCOIN_VERSION}-${ARCH}.tar.gz -C /opt && \
    mv /opt/bitcoin-${BITCOIN_VERSION}/bin/* ${BITCOIN_BIN}/ && \
    rm -rf /opt/bitcoin-${BITCOIN_VERSION} /opt/bitcoin-${BITCOIN_VERSION}-${ARCH}.tar.gz

EXPOSE 8332 8333 18332 18333

VOLUME ["${BITCOIN_DATA}"]

WORKDIR ${BITCOIN_ROOT}

ENTRYPOINT ["bitcoind"]
CMD ["-printtoconsole", "-conf=/opt/bitcoind/bitcoin.conf"]