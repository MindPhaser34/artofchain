# Ethereum node

## Run Ethereum node (Geth + Nimbus)

First, we create the folders and set permissions:

```shell
mkdir -p ./nimbus-data
chmod 700 ./nimbus-data
chown 1000:1000 ./nimbus-data
```

Generate jwt:

```shell
openssl rand -hex 32 > jwt.hex
```

Create docker-compose.yaml
```
services:
  geth:
    image: ethereum/client-go:stable
    container_name: geth
    restart: unless-stopped
    ports:
      - "8545:8545"     # JSON-RPC
      - "8546:8546"     # WebSocket
      - "30303:30303"   # P2P
    volumes:
      - ./geth-data:/root/.ethereum
      - ./jwt.hex:/jwt.hex:ro
    command:
      - --http
      - --http.addr=0.0.0.0
      - --http.port=8545
      - --http.api=eth,net,web3,engine,txpool,debug
      - --http.vhosts=*
      - --ws
      - --ws.addr=0.0.0.0
      - --ws.port=8546
      - --ws.api=eth,net,web3
      - --authrpc.addr=0.0.0.0
      - --authrpc.port=8551
      - --authrpc.vhosts=*
      - --authrpc.jwtsecret=/jwt.hex
      - --db.engine=pebble
      - --maxpeers=300
      - --metrics
      - --metrics.addr=0.0.0.0
      - --metrics.port=6060

  nimbus:
    image: statusim/nimbus-eth2:multiarch-latest
    container_name: nimbus
    restart: unless-stopped
    depends_on:
      - geth
    ports:
      - "9000:9000"     # P2P
      - "5052:5052"     # REST API
    volumes:
      - ./nimbus-data:/data
      - ./jwt.hex:/jwt.hex:ro
    command:
      - --network=mainnet
      - --data-dir=/data
      - --el=http://geth:8551
      - --jwt-secret=/jwt.hex
      - --rest
      - --rest-address=0.0.0.0
      - --history=prune
      - --metrics
      - --metrics-address=0.0.0.0
      - --metrics-port=8001
```

Run node
```shell
docker compose up -d
```

Done.