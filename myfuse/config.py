"""
Configuration settings for the blockchain-backed FUSE filesystem.
"""

import os

# IPFS Configuration
IPFS_HOST = 'localhost'
IPFS_PORT = 5001
IPFS_API_URL = '/ip4/127.0.0.1/tcp/5001'

# File System Configuration
CHUNK_SIZE = 1024  # 1KB chunks
MOUNT_POINT = './mountpoint'
BLOCKCHAIN_FILE = './blockchain.json'
LOG_FILE = './logs.txt'

# Blockchain Configuration
DIFFICULTY = 3  # Number of leading zeros for PoW
MAX_NONCE = 1000000  # Maximum nonce value for PoW

# File System Permissions
DEFAULT_FILE_MODE = 0o644
DEFAULT_DIR_MODE = 0o755

# Ensure required directories exist
os.makedirs(os.path.dirname(BLOCKCHAIN_FILE), exist_ok=True)
os.makedirs(MOUNT_POINT, exist_ok=True)
