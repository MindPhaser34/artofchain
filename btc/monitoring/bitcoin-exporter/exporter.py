#!/usr/bin/env python3
"""
Bitcoin Prometheus Exporter
Exports Bitcoin node metrics for Prometheus monitoring
"""

import os
import time
import json
import requests
from prometheus_client import start_http_server, Gauge, Counter, Info

# Configuration from environment
RPC_HOST = os.getenv('BITCOIN_RPC_HOST', 'bitcoind')
RPC_PORT = os.getenv('BITCOIN_RPC_PORT', '8332')
RPC_USER = os.getenv('BITCOIN_RPC_USER', 'admin')
RPC_PASS = os.getenv('BITCOIN_RPC_PASS', 'mysecretpassword123')
EXPORTER_PORT = int(os.getenv('EXPORTER_PORT', '9332'))
SCRAPE_INTERVAL = int(os.getenv('SCRAPE_INTERVAL', '15'))

# Prometheus metrics
# Blockchain info
BLOCK_HEIGHT = Gauge('bitcoin_block_height', 'Current block height of the node')
BLOCK_HEADERS = Gauge('bitcoin_block_headers', 'Number of block headers')
VERIFICATION_PROGRESS = Gauge('bitcoin_verification_progress', 'Blockchain verification progress (0-1)')
CHAIN_SIZE_BYTES = Gauge('bitcoin_chain_size_bytes', 'Size of blockchain on disk in bytes')
DIFFICULTY = Gauge('bitcoin_difficulty', 'Current mining difficulty')
CHAIN_WORK = Gauge('bitcoin_chain_work', 'Total chain work (log2)')

# Network info
CONNECTIONS_IN = Gauge('bitcoin_connections_in', 'Number of inbound connections')
CONNECTIONS_OUT = Gauge('bitcoin_connections_out', 'Number of outbound connections')
CONNECTIONS_TOTAL = Gauge('bitcoin_connections_total', 'Total number of connections')
NETWORK_BYTES_RECV = Gauge('bitcoin_network_bytes_recv_total', 'Total bytes received')
NETWORK_BYTES_SENT = Gauge('bitcoin_network_bytes_sent_total', 'Total bytes sent')

# Mempool info
MEMPOOL_SIZE = Gauge('bitcoin_mempool_size', 'Number of transactions in mempool')
MEMPOOL_BYTES = Gauge('bitcoin_mempool_bytes', 'Size of mempool in bytes')
MEMPOOL_USAGE = Gauge('bitcoin_mempool_usage', 'Total memory usage for mempool')
MEMPOOL_MIN_FEE = Gauge('bitcoin_mempool_min_fee', 'Minimum fee rate for tx to be accepted')

# Peer info
PEER_COUNT_BY_VERSION = Gauge('bitcoin_peer_count_by_version', 'Number of peers by version', ['version'])

# External blockchain height (from blockchain.info API)
EXTERNAL_BLOCK_HEIGHT = Gauge('bitcoin_external_block_height', 'Current block height from external API')
SYNC_LAG = Gauge('bitcoin_sync_lag', 'Blocks behind external chain (external - local)')

# Node info
NODE_INFO = Info('bitcoin_node', 'Bitcoin node information')

# Version metrics (numeric for easier display)
BITCOIN_VERSION = Gauge('bitcoin_version', 'Bitcoin Core version as number (e.g., 300200 for 30.2.0)')
BITCOIN_VERSION_MAJOR = Gauge('bitcoin_version_major', 'Bitcoin Core major version')
BITCOIN_VERSION_MINOR = Gauge('bitcoin_version_minor', 'Bitcoin Core minor version')
PROTOCOL_VERSION = Gauge('bitcoin_protocol_version', 'Bitcoin protocol version')

# Error counter
RPC_ERRORS = Counter('bitcoin_rpc_errors_total', 'Total number of RPC errors')


def rpc_call(method, params=None):
    """Make RPC call to Bitcoin node"""
    url = f"http://{RPC_HOST}:{RPC_PORT}"
    headers = {'content-type': 'application/json'}
    payload = {
        "jsonrpc": "2.0",
        "id": "exporter",
        "method": method,
        "params": params or []
    }

    try:
        response = requests.post(
            url,
            data=json.dumps(payload),
            headers=headers,
            auth=(RPC_USER, RPC_PASS),
            timeout=30
        )
        response.raise_for_status()
        result = response.json()
        if 'error' in result and result['error']:
            raise Exception(f"RPC Error: {result['error']}")
        return result.get('result')
    except Exception as e:
        RPC_ERRORS.inc()
        print(f"RPC call failed for {method}: {e}")
        return None


def get_external_block_height():
    """Get current block height from blockchain.info API"""
    try:
        response = requests.get(
            'https://blockchain.info/q/getblockcount',
            timeout=10
        )
        response.raise_for_status()
        return int(response.text)
    except Exception as e:
        print(f"Failed to get external block height: {e}")
        return None


def collect_blockchain_info():
    """Collect blockchain information"""
    info = rpc_call('getblockchaininfo')
    if info:
        BLOCK_HEIGHT.set(info.get('blocks', 0))
        BLOCK_HEADERS.set(info.get('headers', 0))
        VERIFICATION_PROGRESS.set(info.get('verificationprogress', 0))
        DIFFICULTY.set(info.get('difficulty', 0))

        # Calculate log2 of chainwork for reasonable metric value
        chainwork_hex = info.get('chainwork', '0')
        if chainwork_hex:
            chainwork_int = int(chainwork_hex, 16)
            if chainwork_int > 0:
                import math
                CHAIN_WORK.set(math.log2(chainwork_int))

        # Get chain size
        size_info = rpc_call('gettxoutsetinfo')
        if size_info:
            CHAIN_SIZE_BYTES.set(size_info.get('disk_size', 0))

        return info.get('blocks', 0)
    return None


def collect_network_info():
    """Collect network information"""
    info = rpc_call('getnetworkinfo')
    if info:
        CONNECTIONS_IN.set(info.get('connections_in', 0))
        CONNECTIONS_OUT.set(info.get('connections_out', 0))
        CONNECTIONS_TOTAL.set(info.get('connections', 0))

        # Version info
        version = info.get('version', 0)
        protocol_version = info.get('protocolversion', 0)
        subversion = info.get('subversion', '')

        # Set version metrics
        BITCOIN_VERSION.set(version)
        PROTOCOL_VERSION.set(protocol_version)

        # Parse version: 300200 -> major=30, minor=2
        # Bitcoin Core version format: MMmmpp (Major, minor, patch) * 10000
        if version > 0:
            major = version // 10000
            minor = (version % 10000) // 100
            BITCOIN_VERSION_MAJOR.set(major)
            BITCOIN_VERSION_MINOR.set(minor)

        NODE_INFO.info({
            'version': str(version),
            'version_string': f"{version // 10000}.{(version % 10000) // 100}.{version % 100}",
            'subversion': subversion,
            'protocol_version': str(protocol_version),
            'network': 'mainnet'
        })

    # Get network totals
    totals = rpc_call('getnettotals')
    if totals:
        NETWORK_BYTES_RECV.set(totals.get('totalbytesrecv', 0))
        NETWORK_BYTES_SENT.set(totals.get('totalbytessent', 0))


def collect_mempool_info():
    """Collect mempool information"""
    info = rpc_call('getmempoolinfo')
    if info:
        MEMPOOL_SIZE.set(info.get('size', 0))
        MEMPOOL_BYTES.set(info.get('bytes', 0))
        MEMPOOL_USAGE.set(info.get('usage', 0))
        MEMPOOL_MIN_FEE.set(info.get('mempoolminfee', 0))


def collect_peer_info():
    """Collect peer information"""
    peers = rpc_call('getpeerinfo')
    if peers:
        version_counts = {}
        for peer in peers:
            version = peer.get('subver', 'unknown')
            version_counts[version] = version_counts.get(version, 0) + 1

        for version, count in version_counts.items():
            PEER_COUNT_BY_VERSION.labels(version=version).set(count)


def collect_external_height(local_height):
    """Collect external block height and calculate sync lag"""
    external_height = get_external_block_height()
    if external_height:
        EXTERNAL_BLOCK_HEIGHT.set(external_height)
        if local_height:
            lag = external_height - local_height
            SYNC_LAG.set(max(0, lag))


def collect_metrics():
    """Collect all metrics"""
    print("Collecting metrics...")

    local_height = collect_blockchain_info()
    collect_network_info()
    collect_mempool_info()
    collect_peer_info()
    collect_external_height(local_height)

    print(f"Metrics collected. Local height: {local_height}")


def main():
    """Main function"""
    print(f"Starting Bitcoin Prometheus Exporter on port {EXPORTER_PORT}")
    print(f"Connecting to Bitcoin RPC at {RPC_HOST}:{RPC_PORT}")

    # Start HTTP server for Prometheus
    start_http_server(EXPORTER_PORT)
    print(f"Exporter running on http://0.0.0.0:{EXPORTER_PORT}/metrics")

    # Collect metrics in a loop
    while True:
        try:
            collect_metrics()
        except Exception as e:
            print(f"Error collecting metrics: {e}")
            RPC_ERRORS.inc()

        time.sleep(SCRAPE_INTERVAL)


if __name__ == '__main__':
    main()
