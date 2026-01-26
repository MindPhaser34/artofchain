# Ethereum Node with Monitoring Stack

Ethereum full node (Geth + Nimbus) with Prometheus metrics exporter and Grafana dashboard.

## Components

| Service | Version | Port | Description |
|---------|---------|------|-------------|
| Geth | v1.16.8 | 8545 (RPC), 8546 (WS), 30303 (P2P), 6060 (Metrics) | Execution layer client |
| Nimbus | multiarch-v25.12.0 | 5052 (REST), 9000 (P2P), 8001 (Metrics) | Consensus layer client |
| ETH Exporter | - | 9333 | Prometheus metrics exporter |
| Prometheus | v3.5.1 | 9090 | Metrics collection |
| Grafana | 12.3.1 | 3000 | Visualization |

## Quick Start

```bash
# Create data directories
mkdir -p ./nimbus-data ./geth-data

# Generate JWT secret
openssl rand -hex 32 > jwt.hex

# Start all services
docker-compose up -d

# Check status
docker-compose ps
```

## Access

- **Grafana**: http://localhost:3000 (admin/admin)
- **Prometheus**: http://localhost:9090
- **Geth RPC**: http://localhost:8545
- **Nimbus REST API**: http://localhost:5052

## Metrics

### Block & Sync

| Metric | Description |
|--------|-------------|
| `eth_block_number` | Current block number (execution layer) |
| `eth_external_block_number` | External block number from Etherscan |
| `eth_sync_lag` | Blocks behind external chain |
| `eth_syncing` | Node syncing status (1=syncing, 0=synced) |
| `eth_beacon_head_slot` | Beacon chain head slot |
| `eth_beacon_sync_distance` | Slots behind in beacon sync |

### Network

| Metric | Description |
|--------|-------------|
| `eth_peer_count` | Number of connected peers (execution) |
| `eth_beacon_peer_count` | Number of connected peers (consensus) |

### Gas & Mempool

| Metric | Description |
|--------|-------------|
| `eth_gas_price_gwei` | Current gas price in Gwei |
| `eth_base_fee_gwei` | Base fee per gas in Gwei |
| `eth_pending_transactions` | Number of pending transactions |
| `eth_queued_transactions` | Number of queued transactions |

### Chain Info

| Metric | Description |
|--------|-------------|
| `eth_chain_id` | Network chain ID |
| `eth_latest_block_timestamp` | Timestamp of latest block |
| `eth_block_time_seconds` | Time since last block |

### Beacon Chain

| Metric | Description |
|--------|-------------|
| `eth_beacon_finalized_epoch` | Last finalized epoch |
| `eth_beacon_justified_epoch` | Last justified epoch |
| `eth_beacon_participation_rate` | Network participation rate |

### Client Info

| Metric | Description |
|--------|-------------|
| `eth_client_info` | Geth client version info |
| `eth_beacon_client_info` | Nimbus client version info |

## Grafana Dashboard

Dashboard is auto-provisioned and available at:
`Dashboards → Ethereum → Ethereum Node Dashboard`

### Sections:
1. **Block & Sync Status** - Node vs external block height comparison
2. **Sync Progress** - Sync lag and beacon chain distance
3. **Network** - Peer connections for both execution and consensus layers
4. **Gas & Mempool** - Gas prices and pending transactions
5. **Beacon Chain** - Finality, epochs, and participation
6. **Errors & Health** - RPC error tracking

## Architecture

```
┌─────────────────┐     ┌──────────────────┐
│      Geth       │────▶│                  │
│  (Execution)    │ RPC │   ETH Exporter   │      ┌─────────────┐
└─────────────────┘     │     (Python)     │─────▶│  Prometheus │
                        │                  │      │   (v3.5.1)  │
┌─────────────────┐     │                  │      └──────┬──────┘
│     Nimbus      │────▶│                  │             │
│  (Consensus)    │ REST└──────────────────┘             ▼
└─────────────────┘                               ┌─────────────┐
                                                  │   Grafana   │
                                                  │  (12.3.1)   │
                                                  └─────────────┘
```

## Ports

| Port | Service | Protocol |
|------|---------|----------|
| 8545 | Geth JSON-RPC | HTTP |
| 8546 | Geth WebSocket | WS |
| 30303 | Geth P2P | TCP/UDP |
| 6060 | Geth Metrics | HTTP |
| 5052 | Nimbus REST API | HTTP |
| 9000 | Nimbus P2P | TCP/UDP |
| 8001 | Nimbus Metrics | HTTP |
| 9090 | Prometheus | HTTP |
| 9333 | ETH Exporter | HTTP |
| 3000 | Grafana | HTTP |

## Troubleshooting

### Check logs

```bash
# Geth node
docker logs geth

# Nimbus node
docker logs nimbus

# Exporter
docker logs eth-exporter

# All services
docker compose logs -f
```

### Verify metrics

```bash
# Check exporter
curl http://localhost:9333/metrics

# Check Prometheus targets
curl http://localhost:9090/api/v1/targets

# Check current block
curl http://localhost:9090/api/v1/query?query=eth_block_number
```

### Restart services

```bash
docker compose restart
```

## License

MIT
