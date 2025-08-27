"""
Verification and setup script that ensures all files exist before testing.
"""

import os
import sys

def create_minimal_blockchain():
    """Create a minimal blockchain implementation for testing."""
    content = '''"""
Minimal blockchain implementation for testing.
"""

import json
import hashlib
import datetime
from dataclasses import dataclass, asdict
from typing import List, Dict, Any

@dataclass
class Block:
    """Represents a block in the blockchain."""
    index: int
    timestamp: str
    filename: str
    file_size: int
    chunk_hash: str
    ipfs_hash: str
    previous_hash: str
    nonce: int = 0
    hash: str = ""
    
    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Block':
        return cls(**data)

class Blockchain:
    """Simple blockchain for file integrity."""
    
    def __init__(self, blockchain_file: str = './blockchain.json'):
        self.blockchain_file = blockchain_file
        self.chain: List[Block] = []
        self.load_blockchain()
        
        if not self.chain:
            self.create_genesis_block()
    
    def create_genesis_block(self) -> Block:
        """Create the genesis block."""
        genesis_block = Block(
            index=0,
            timestamp=datetime.datetime.now().isoformat(),
            filename="GENESIS",
            file_size=0,
            chunk_hash="0" * 64,
            ipfs_hash="",
            previous_hash="0" * 64,
            nonce=0
        )
        genesis_block.hash = self.calculate_hash(genesis_block)
        self.chain.append(genesis_block)
        self.save_blockchain()
        return genesis_block
    
    def calculate_hash(self, block: Block) -> str:
        """Calculate SHA-256 hash of a block."""
        block_string = (
            str(block.index) +
            block.timestamp +
            block.filename +
            str(block.file_size) +
            block.chunk_hash +
            block.ipfs_hash +
            block.previous_hash +
            str(block.nonce)
        )
        return hashlib.sha256(block_string.encode()).hexdigest()
    
    def proof_of_work(self, block: Block) -> int:
        """Simple proof of work."""
        target = "000"  # 3 leading zeros
        
        for nonce in range(100000):
            block.nonce = nonce
            hash_result = self.calculate_hash(block)
            
            if hash_result.startswith(target):
                return nonce
        
        return 0
    
    def add_block(self, filename: str, file_size: int, chunk_hash: str, ipfs_hash: str) -> Block:
        """Add a new block to the blockchain."""
        previous_block = self.get_latest_block()
        
        new_block = Block(
            index=len(self.chain),
            timestamp=datetime.datetime.now().isoformat(),
            filename=filename,
            file_size=file_size,
            chunk_hash=chunk_hash,
            ipfs_hash=ipfs_hash,
            previous_hash=previous_block.hash
        )
        
        new_block.nonce = self.proof_of_work(new_block)
        new_block.hash = self.calculate_hash(new_block)
        
        self.chain.append(new_block)
        self.save_blockchain()
        return new_block
    
    def get_latest_block(self) -> Block:
        """Get the latest block in the chain."""
        return self.chain[-1] if self.chain else None
    
    def get_file_blocks(self, filename: str) -> List[Block]:
        """Get all blocks for a specific file."""
        return [block for block in self.chain if block.filename == filename]
    
    def validate_chain(self) -> bool:
        """Validate the entire blockchain."""
        for i in range(1, len(self.chain)):
            current_block = self.chain[i]
            previous_block = self.chain[i - 1]
            
            if current_block.hash != self.calculate_hash(current_block):
                return False
            
            if current_block.previous_hash != previous_block.hash:
                return False
        
        return True
    
    def detect_tampering(self, filename: str) -> List[int]:
        """Detect tampering in blocks for a specific file."""
        tampered_blocks = []
        file_blocks = self.get_file_blocks(filename)
        
        for block in file_blocks:
            if block.hash != self.calculate_hash(block):
                tampered_blocks.append(block.index)
        
        return tampered_blocks
    
    def save_blockchain(self):
        """Save blockchain to file."""
        try:
            blockchain_data = {
                'chain': [block.to_dict() for block in self.chain],
                'length': len(self.chain)
            }
            
            with open(self.blockchain_file, 'w') as f:
                json.dump(blockchain_data, f, indent=2)
        except Exception as e:
            print(f"Error saving blockchain: {e}")
    
    def load_blockchain(self):
        """Load blockchain from file."""
        try:
            if os.path.exists(self.blockchain_file):
                with open(self.blockchain_file, 'r') as f:
                    blockchain_data = json.load(f)
                
                self.chain = [Block.from_dict(block_data) for block_data in blockchain_data['chain']]
        except Exception as e:
            print(f"Error loading blockchain: {e}")
            self.chain = []
    
    def get_blockchain_info(self) -> Dict[str, Any]:
        """Get blockchain information."""
        return {
            'total_blocks': len(self.chain),
            'latest_block_hash': self.get_latest_block().hash if self.chain else None,
            'is_valid': self.validate_chain(),
            'files': list(set(block.filename for block in self.chain if block.filename != "GENESIS"))
        }

# Global blockchain instance
blockchain = Blockchain()
'''
    
    os.makedirs('myfuse', exist_ok=True)
    with open('myfuse/blockchain.py', 'w') as f:
        f.write(content)
    print("✅ Created myfuse/blockchain.py")

def create_minimal_ipfs_client():
    """Create a minimal IPFS client for testing."""
    content = '''"""
Minimal IPFS client simulation for testing.
"""

import hashlib
from typing import Optional

class IPFSClient:
    """Simulated IPFS client for testing."""
    
    def __init__(self):
        self.storage = {}  # Simulate IPFS storage
    
    def upload_chunk(self, chunk_data: bytes) -> Optional[str]:
        """Simulate uploading a chunk to IPFS."""
        # Create a hash-based identifier
        chunk_hash = hashlib.sha256(chunk_data).hexdigest()
        ipfs_hash = f"Qm{chunk_hash[:40]}"  # Simulate IPFS hash format
        
        # Store in simulated IPFS
        self.storage[ipfs_hash] = chunk_data
        
        return ipfs_hash
    
    def download_chunk(self, ipfs_hash: str) -> Optional[bytes]:
        """Simulate downloading a chunk from IPFS."""
        return self.storage.get(ipfs_hash, b"simulated_chunk_data")
    
    def verify_chunk(self, chunk_data: bytes, expected_hash: str) -> bool:
        """Verify chunk integrity by comparing SHA-256 hashes."""
        actual_hash = hashlib.sha256(chunk_data).hexdigest()
        return actual_hash == expected_hash
    
    def is_connected(self) -> bool:
        """Simulate connection status."""
        return True

# Global IPFS client instance
ipfs_client = IPFSClient()
'''
    
    with open('myfuse/ipfs_client.py', 'w') as f:
        f.write(content)
    print("✅ Created myfuse/ipfs_client.py")

def create_minimal_config():
    """Create a minimal config file."""
    content = '''"""
Configuration settings for the blockchain filesystem.
"""

# IPFS Configuration
IPFS_HOST = 'localhost'
IPFS_PORT = 5001
IPFS_API_URL = f'http://{IPFS_HOST}:{IPFS_PORT}'

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
'''
    
    with open('myfuse/config.py', 'w') as f:
        f.write(content)
    print("✅ Created myfuse/config.py")

def create_minimal_logger():
    """Create a minimal logger."""
    content = '''"""
Simple logging for the blockchain filesystem.
"""

import logging
import datetime

class FileSystemLogger:
    """Simple logger for file system operations."""
    
    def __init__(self, log_file: str = './logs.txt'):
        self.log_file = log_file
        logging.basicConfig(level=logging.INFO)
        self.logger = logging.getLogger(__name__)
    
    def log_mount(self, mount_point: str):
        self.logger.info(f"MOUNT: Filesystem mounted at {mount_point}")
    
    def log_write(self, filename: str, size: int, chunks: int):
        self.logger.info(f"WRITE: {filename} - Size: {size} bytes, Chunks: {chunks}")
    
    def log_read(self, filename: str, size: int, chunks: int):
        self.logger.info(f"READ: {filename} - Size: {size} bytes, Chunks: {chunks}")
    
    def log_error(self, operation: str, error: str):
        self.logger.error(f"ERROR: {operation} - {error}")

# Global logger instance
fs_logger = FileSystemLogger()
'''
    
    with open('myfuse/log.py', 'w') as f:
        f.write(content)
    print("✅ Created myfuse/log.py")

def create_init_file():
    """Create __init__.py file."""
    content = '''"""
Blockchain FUSE filesystem package.
"""
'''
    with open('myfuse/__init__.py', 'w') as f:
        f.write(content)
    print("✅ Created myfuse/__init__.py")

def verify_and_setup():
    """Verify setup and create missing files."""
    print("🔍 Verifying project setup...")
    
    # Create directories
    os.makedirs('myfuse', exist_ok=True)
    os.makedirs('mountpoint', exist_ok=True)
    
    # Check and create required files
    required_files = {
        'myfuse/blockchain.py': create_minimal_blockchain,
        'myfuse/ipfs_client.py': create_minimal_ipfs_client,
        'myfuse/config.py': create_minimal_config,
        'myfuse/log.py': create_minimal_logger,
        'myfuse/__init__.py': create_init_file,
    }
    
    missing_files = []
    for file_path in required_files:
        if not os.path.exists(file_path):
            missing_files.append(file_path)
    
    if missing_files:
        print(f"📝 Creating {len(missing_files)} missing files...")
        for file_path, create_func in required_files.items():
            if not os.path.exists(file_path):
                create_func()
        print("✅ All required files created!")
    else:
        print("✅ All required files already exist!")
    
    return True

def main():
    """Main verification function."""
    print("🔧 Blockchain FUSE Filesystem - Setup Verification")
    print("=" * 55)
    
    try:
        if verify_and_setup():
            print("\n🎉 Setup verification completed successfully!")
            print("\n🎯 You can now run:")
            print("   python scripts/quick_test.py")
            print("   python scripts/demo.py")
            print("   python scripts/run_guide.py")
            return True
        else:
            print("\n❌ Setup verification failed!")
            return False
    except Exception as e:
        print(f"\n💥 Setup verification crashed: {e}")
        return False

if __name__ == '__main__':
    success = main()
    sys.exit(0 if success else 1)
