"""
Script to create all the blockchain FUSE filesystem project files.
This script writes all the necessary Python files to the filesystem.
"""

import os

def create_file(filepath, content):
    """Create a file with the given content."""
    # Ensure directory exists
    os.makedirs(os.path.dirname(filepath), exist_ok=True)
    
    # Write the file
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(content)
    
    print(f"✅ Created: {filepath}")

def create_config_py():
    """Create the config.py file."""
    content = '''"""
Configuration settings for the blockchain-backed FUSE filesystem.
"""

import os

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

# Ensure required directories exist
os.makedirs(os.path.dirname(BLOCKCHAIN_FILE), exist_ok=True)
os.makedirs(MOUNT_POINT, exist_ok=True)
'''
    create_file('myfuse/config.py', content)

def create_log_py():
    """Create the log.py file."""
    content = '''"""
Logging system for the blockchain-backed FUSE filesystem.
"""

import logging
import datetime
from typing import Optional
from config import LOG_FILE

class FileSystemLogger:
    """Logger for file system operations."""
    
    def __init__(self, log_file: str = LOG_FILE):
        """Initialize the logger."""
        self.log_file = log_file
        self.setup_logger()
    
    def setup_logger(self):
        """Set up the logging configuration."""
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler(self.log_file),
                logging.StreamHandler()
            ]
        )
        self.logger = logging.getLogger(__name__)
    
    def log_mount(self, mount_point: str):
        """Log filesystem mount operation."""
        self.logger.info(f"MOUNT: Filesystem mounted at {mount_point}")
    
    def log_unmount(self, mount_point: str):
        """Log filesystem unmount operation."""
        self.logger.info(f"UNMOUNT: Filesystem unmounted from {mount_point}")
    
    def log_write(self, filename: str, size: int, chunks: int):
        """Log file write operation."""
        self.logger.info(f"WRITE: {filename} - Size: {size} bytes, Chunks: {chunks}")
    
    def log_read(self, filename: str, size: int, chunks: int):
        """Log file read operation."""
        self.logger.info(f"READ: {filename} - Size: {size} bytes, Chunks: {chunks}")
    
    def log_verify(self, filename: str, status: str, details: Optional[str] = None):
        """Log file verification operation."""
        message = f"VERIFY: {filename} - Status: {status}"
        if details:
            message += f" - {details}"
        self.logger.info(message)
    
    def log_error(self, operation: str, error: str):
        """Log error operations."""
        self.logger.error(f"ERROR: {operation} - {error}")
    
    def log_tamper_detected(self, filename: str, block_index: int):
        """Log tamper detection."""
        self.logger.warning(f"TAMPER DETECTED: {filename} - Block {block_index}")
    
    def log_blockchain_operation(self, operation: str, details: str):
        """Log blockchain operations."""
        self.logger.info(f"BLOCKCHAIN: {operation} - {details}")

# Global logger instance
fs_logger = FileSystemLogger()
'''
    create_file('myfuse/log.py', content)

def create_ipfs_client_py():
    """Create the ipfs_client.py file."""
    content = '''"""
IPFS client for uploading and downloading file chunks.
"""

import hashlib
from typing import Optional, bytes
from config import IPFS_API_URL
from log import fs_logger

try:
    import ipfshttpclient
    IPFS_AVAILABLE = True
except ImportError:
    IPFS_AVAILABLE = False
    print("Warning: ipfshttpclient not installed. Install with: pip install ipfshttpclient")

class IPFSClient:
    """Client for interacting with IPFS."""
    
    def __init__(self, api_url: str = IPFS_API_URL):
        """Initialize IPFS client."""
        self.api_url = api_url
        self.client = None
        if IPFS_AVAILABLE:
            self.connect()
    
    def connect(self) -> bool:
        """Connect to IPFS daemon."""
        if not IPFS_AVAILABLE:
            fs_logger.log_error("IPFS_CONNECT", "ipfshttpclient not installed")
            return False
            
        try:
            self.client = ipfshttpclient.connect(self.api_url)
            # Test connection
            self.client.version()
            fs_logger.log_blockchain_operation("IPFS_CONNECT", f"Connected to {self.api_url}")
            return True
        except Exception as e:
            fs_logger.log_error("IPFS_CONNECT", str(e))
            return False
    
    def upload_chunk(self, chunk_data: bytes) -> Optional[str]:
        """Upload a chunk to IPFS and return the hash."""
        if not IPFS_AVAILABLE or not self.client:
            # Simulate IPFS hash for testing
            import hashlib
            simulated_hash = hashlib.sha256(chunk_data).hexdigest()[:46]  # IPFS-like hash
            fs_logger.log_blockchain_operation("IPFS_UPLOAD_SIM", f"Simulated upload: {simulated_hash}")
            return f"Qm{simulated_hash}"
            
        try:
            result = self.client.add_bytes(chunk_data)
            ipfs_hash = result
            fs_logger.log_blockchain_operation("IPFS_UPLOAD", f"Chunk uploaded: {ipfs_hash}")
            return ipfs_hash
        except Exception as e:
            fs_logger.log_error("IPFS_UPLOAD", str(e))
            return None
    
    def download_chunk(self, ipfs_hash: str) -> Optional[bytes]:
        """Download a chunk from IPFS using its hash."""
        if not IPFS_AVAILABLE or not self.client:
            # For simulation, return dummy data
            fs_logger.log_blockchain_operation("IPFS_DOWNLOAD_SIM", f"Simulated download: {ipfs_hash}")
            return b"simulated_chunk_data"
            
        try:
            chunk_data = self.client.cat(ipfs_hash)
            fs_logger.log_blockchain_operation("IPFS_DOWNLOAD", f"Chunk downloaded: {ipfs_hash}")
            return chunk_data
        except Exception as e:
            fs_logger.log_error("IPFS_DOWNLOAD", str(e))
            return None
    
    def verify_chunk(self, chunk_data: bytes, expected_hash: str) -> bool:
        """Verify chunk integrity by comparing SHA-256 hashes."""
        actual_hash = hashlib.sha256(chunk_data).hexdigest()
        return actual_hash == expected_hash
    
    def is_connected(self) -> bool:
        """Check if connected to IPFS."""
        if not IPFS_AVAILABLE:
            return False
        try:
            if self.client:
                self.client.version()
                return True
        except:
            pass
        return False

# Global IPFS client instance
ipfs_client = IPFSClient()
'''
    create_file('myfuse/ipfs_client.py', content)

def create_blockchain_py():
    """Create the blockchain.py file."""
    content = '''"""
Blockchain implementation for file integrity verification.
"""

import json
import hashlib
import datetime
import os
from typing import List, Dict, Optional, Any
from dataclasses import dataclass, asdict
from config import BLOCKCHAIN_FILE, DIFFICULTY, MAX_NONCE
from log import fs_logger

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
        """Convert block to dictionary."""
        return asdict(self)
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Block':
        """Create block from dictionary."""
        return cls(**data)

class Blockchain:
    """Blockchain for maintaining file integrity."""
    
    def __init__(self, blockchain_file: str = BLOCKCHAIN_FILE):
        """Initialize blockchain."""
        self.blockchain_file = blockchain_file
        self.chain: List[Block] = []
        self.load_blockchain()
        
        # Create genesis block if chain is empty
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
        
        fs_logger.log_blockchain_operation("GENESIS", "Genesis block created")
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
        """Perform proof of work to find a valid nonce."""
        target = "0" * DIFFICULTY
        
        for nonce in range(MAX_NONCE):
            block.nonce = nonce
            hash_result = self.calculate_hash(block)
            
            if hash_result.startswith(target):
                fs_logger.log_blockchain_operation("POW", f"Nonce found: {nonce}, Hash: {hash_result}")
                return nonce
        
        fs_logger.log_error("POW", "Max nonce reached without finding valid hash")
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
        
        # Perform proof of work
        new_block.nonce = self.proof_of_work(new_block)
        new_block.hash = self.calculate_hash(new_block)
        
        self.chain.append(new_block)
        self.save_blockchain()
        
        fs_logger.log_blockchain_operation("ADD_BLOCK", f"Block {new_block.index} added for {filename}")
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
            
            # Check if current block's hash is valid
            if current_block.hash != self.calculate_hash(current_block):
                fs_logger.log_error("VALIDATE", f"Invalid hash at block {i}")
                return False
            
            # Check if current block points to previous block
            if current_block.previous_hash != previous_block.hash:
                fs_logger.log_error("VALIDATE", f"Invalid previous hash at block {i}")
                return False
            
            # Check proof of work
            if not current_block.hash.startswith("0" * DIFFICULTY):
                fs_logger.log_error("VALIDATE", f"Invalid proof of work at block {i}")
                return False
        
        fs_logger.log_blockchain_operation("VALIDATE", "Blockchain validation successful")
        return True
    
    def detect_tampering(self, filename: str) -> List[int]:
        """Detect tampering in blocks for a specific file."""
        tampered_blocks = []
        file_blocks = self.get_file_blocks(filename)
        
        for block in file_blocks:
            if block.hash != self.calculate_hash(block):
                tampered_blocks.append(block.index)
                fs_logger.log_tamper_detected(filename, block.index)
        
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
            fs_logger.log_error("SAVE_BLOCKCHAIN", str(e))
    
    def load_blockchain(self):
        """Load blockchain from file."""
        try:
            if os.path.exists(self.blockchain_file):
                with open(self.blockchain_file, 'r') as f:
                    blockchain_data = json.load(f)
                
                self.chain = [Block.from_dict(block_data) for block_data in blockchain_data['chain']]
                fs_logger.log_blockchain_operation("LOAD", f"Loaded {len(self.chain)} blocks")
            
        except Exception as e:
            fs_logger.log_error("LOAD_BLOCKCHAIN", str(e))
            self.chain = []
    
    def get_blockchain_info(self) -> Dict[str, Any]:
        """Get blockchain information."""
        return {
            'total_blocks': len(self.chain),
            'latest_block_hash': self.get_latest_block().hash if self.chain else None,
            'is_valid': self.validate_chain(),
            'files': list(set(block.filename for block in self.chain if block.filename != "GENESIS"))
        }
    
    def print_blockchain(self):
        """Print the entire blockchain."""
        print("\\n" + "="*80)
        print("BLOCKCHAIN CONTENTS")
        print("="*80)
        
        for block in self.chain:
            print(f"\\nBlock {block.index}:")
            print(f"  Timestamp: {block.timestamp}")
            print(f"  Filename: {block.filename}")
            print(f"  File Size: {block.file_size}")
            print(f"  Chunk Hash: {block.chunk_hash[:16]}...")
            print(f"  IPFS Hash: {block.ipfs_hash}")
            print(f"  Previous Hash: {block.previous_hash[:16]}...")
            print(f"  Nonce: {block.nonce}")
            print(f"  Hash: {block.hash[:16]}...")
        
        print("\\n" + "="*80)

# Global blockchain instance
blockchain = Blockchain()
'''
    create_file('myfuse/blockchain.py', content)

def create_main_py():
    """Create the main.py file."""
    content = '''"""
Main FUSE filesystem implementation for blockchain-backed storage.
"""

import os
import sys
import errno
import hashlib
from typing import Dict, List, Optional

try:
    from fuse import FUSE, FuseOSError, Operations
    FUSE_AVAILABLE = True
except ImportError:
    FUSE_AVAILABLE = False
    print("Warning: fusepy not installed. Install with: pip install fusepy")
    
    # Mock classes for testing
    class FuseOSError(Exception):
        def __init__(self, errno_code):
            self.errno = errno_code
    
    class Operations:
        pass
    
    def FUSE(*args, **kwargs):
        print("FUSE not available - this is a mock implementation")

from config import CHUNK_SIZE, MOUNT_POINT, DEFAULT_FILE_MODE, DEFAULT_DIR_MODE
from blockchain import blockchain
from ipfs_client import ipfs_client
from log import fs_logger

class BlockchainFUSE(Operations):
    """FUSE filesystem with blockchain-backed storage."""
    
    def __init__(self):
        """Initialize the filesystem."""
        self.files: Dict[str, Dict] = {}  # In-memory file metadata
        fs_logger.log_mount(MOUNT_POINT)
    
    def getattr(self, path: str, fh=None):
        """Get file attributes."""
        if path == '/':
            # Root directory attributes
            return {
                'st_mode': DEFAULT_DIR_MODE | 0o040000,  # Directory
                'st_nlink': 2,
                'st_size': 0,
                'st_ctime': 0,
                'st_mtime': 0,
                'st_atime': 0,
            }
        
        filename = path[1:]  # Remove leading slash
        
        if filename in self.files:
            file_info = self.files[filename]
            return {
                'st_mode': DEFAULT_FILE_MODE | 0o100000,  # Regular file
                'st_nlink': 1,
                'st_size': file_info['size'],
                'st_ctime': file_info['ctime'],
                'st_mtime': file_info['mtime'],
                'st_atime': file_info['atime'],
            }
        
        # Check if file exists in blockchain
        file_blocks = blockchain.get_file_blocks(filename)
        if file_blocks:
            total_size = sum(block.file_size for block in file_blocks)
            
            # Add to in-memory cache
            self.files[filename] = {
                'size': total_size,
                'ctime': 0,
                'mtime': 0,
                'atime': 0,
            }
            
            return {
                'st_mode': DEFAULT_FILE_MODE | 0o100000,
                'st_nlink': 1,
                'st_size': total_size,
                'st_ctime': 0,
                'st_mtime': 0,
                'st_atime': 0,
            }
        
        raise FuseOSError(errno.ENOENT)
    
    def readdir(self, path: str, fh):
        """Read directory contents."""
        if path != '/':
            raise FuseOSError(errno.ENOENT)
        
        # Get files from in-memory cache
        files = list(self.files.keys())
        
        # Get files from blockchain
        blockchain_files = set()
        for block in blockchain.chain:
            if block.filename != "GENESIS":
                blockchain_files.add(block.filename)
        
        # Combine both sources
        all_files = set(files) | blockchain_files
        
        return ['.', '..'] + list(all_files)
    
    def read(self, path: str, size: int, offset: int, fh):
        """Read file data."""
        filename = path[1:]  # Remove leading slash
        
        try:
            # Get file blocks from blockchain
            file_blocks = blockchain.get_file_blocks(filename)
            if not file_blocks:
                raise FuseOSError(errno.ENOENT)
            
            # Sort blocks by index to maintain order
            file_blocks.sort(key=lambda b: b.index)
            
            # Detect tampering
            tampered_blocks = blockchain.detect_tampering(filename)
            if tampered_blocks:
                fs_logger.log_error("READ", f"Tampering detected in {filename}")
                raise FuseOSError(errno.EIO)
            
            # Reconstruct file from IPFS chunks
            file_data = b''
            chunk_count = 0
            
            for block in file_blocks:
                # Download chunk from IPFS
                chunk_data = ipfs_client.download_chunk(block.ipfs_hash)
                if chunk_data is None:
                    fs_logger.log_error("READ", f"Failed to download chunk {block.ipfs_hash}")
                    raise FuseOSError(errno.EIO)
                
                # Verify chunk integrity
                if not ipfs_client.verify_chunk(chunk_data, block.chunk_hash):
                    fs_logger.log_error("READ", f"Chunk integrity verification failed for {block.ipfs_hash}")
                    raise FuseOSError(errno.EIO)
                
                file_data += chunk_data
                chunk_count += 1
            
            fs_logger.log_read(filename, len(file_data), chunk_count)
            
            # Return requested portion
            return file_data[offset:offset + size]
            
        except Exception as e:
            fs_logger.log_error("READ", str(e))
            raise FuseOSError(errno.EIO)
    
    def write(self, path: str, data: bytes, offset: int, fh):
        """Write file data."""
        filename = path[1:]  # Remove leading slash
        
        try:
            # For simplicity, we don't support partial writes or appends
            if offset != 0:
                fs_logger.log_error("WRITE", "Partial writes not supported")
                raise FuseOSError(errno.ENOSYS)
            
            # Split data into chunks
            chunks = []
            for i in range(0, len(data), CHUNK_SIZE):
                chunk = data[i:i + CHUNK_SIZE]
                chunks.append(chunk)
            
            # Process each chunk
            chunk_count = 0
            for chunk in chunks:
                # Calculate chunk hash
                chunk_hash = hashlib.sha256(chunk).hexdigest()
                
                # Upload chunk to IPFS
                ipfs_hash = ipfs_client.upload_chunk(chunk)
                if ipfs_hash is None:
                    fs_logger.log_error("WRITE", f"Failed to upload chunk to IPFS")
                    raise FuseOSError(errno.EIO)
                
                # Add block to blockchain
                blockchain.add_block(filename, len(chunk), chunk_hash, ipfs_hash)
                chunk_count += 1
            
            # Update in-memory file info
            self.files[filename] = {
                'size': len(data),
                'ctime': 0,
                'mtime': 0,
                'atime': 0,
            }
            
            fs_logger.log_write(filename, len(data), chunk_count)
            return len(data)
            
        except Exception as e:
            fs_logger.log_error("WRITE", str(e))
            raise FuseOSError(errno.EIO)
    
    def create(self, path: str, mode: int, fi=None):
        """Create a new file."""
        filename = path[1:]  # Remove leading slash
        
        # Initialize empty file
        self.files[filename] = {
            'size': 0,
            'ctime': 0,
            'mtime': 0,
            'atime': 0,
        }
        
        return 0
    
    def truncate(self, path: str, length: int, fh=None):
        """Truncate file (simulate immutability by disallowing)."""
        filename = path[1:]
        fs_logger.log_error("TRUNCATE", f"Truncation not allowed for {filename} (immutable filesystem)")
        raise FuseOSError(errno.EPERM)
    
    def unlink(self, path: str):
        """Delete file (simulate immutability by disallowing)."""
        filename = path[1:]
        fs_logger.log_error("UNLINK", f"Deletion not allowed for {filename} (immutable filesystem)")
        raise FuseOSError(errno.EPERM)
    
    def chmod(self, path: str, mode: int):
        """Change file permissions (not implemented)."""
        return 0
    
    def chown(self, path: str, uid: int, gid: int):
        """Change file ownership (not implemented)."""
        return 0
    
    def utimens(self, path: str, times=None):
        """Update file timestamps (not implemented)."""
        return 0

def main():
    """Main function to mount the filesystem."""
    if not FUSE_AVAILABLE:
        print("Error: FUSE not available. Install with: pip install fusepy")
        sys.exit(1)
    
    if len(sys.argv) != 2:
        print(f"Usage: {sys.argv[0]} <mountpoint>")
        sys.exit(1)
    
    mountpoint = sys.argv[1]
    
    # Check if IPFS is running
    if not ipfs_client.is_connected():
        print("Warning: IPFS daemon is not running. Using simulation mode.")
        print("For full functionality, start IPFS with: ipfs daemon")
    
    # Create mountpoint if it doesn't exist
    os.makedirs(mountpoint, exist_ok=True)
    
    print(f"Mounting blockchain-backed filesystem at {mountpoint}")
    print("Press Ctrl+C to unmount")
    
    try:
        # Mount the filesystem
        fuse = FUSE(
            BlockchainFUSE(),
            mountpoint,
            foreground=True,
            allow_other=True,
            nothreads=True
        )
    except KeyboardInterrupt:
        fs_logger.log_unmount(mountpoint)
        print(f"\\nFilesystem unmounted from {mountpoint}")
    except Exception as e:
        fs_logger.log_error("MOUNT", str(e))
        print(f"Error mounting filesystem: {e}")
        sys.exit(1)

if __name__ == '__main__':
    main()
'''
    create_file('myfuse/main.py', content)

def create_integrity_checker_py():
    """Create the integrity_checker.py file."""
    content = '''"""
CLI utility for verifying blockchain integrity and file verification.
"""

import argparse
import sys
from blockchain import blockchain
from ipfs_client import ipfs_client
from log import fs_logger

class IntegrityChecker:
    """Utility for checking blockchain and file integrity."""
    
    def __init__(self):
        """Initialize the integrity checker."""
        self.blockchain = blockchain
        self.ipfs_client = ipfs_client
    
    def verify_blockchain(self) -> bool:
        """Verify the entire blockchain integrity."""
        print("Verifying blockchain integrity...")
        
        if not self.blockchain.chain:
            print("❌ Blockchain is empty")
            return False
        
        is_valid = self.blockchain.validate_chain()
        
        if is_valid:
            print("✅ Blockchain integrity verified successfully")
            print(f"   Total blocks: {len(self.blockchain.chain)}")
            print(f"   Latest block hash: {self.blockchain.get_latest_block().hash[:16]}...")
        else:
            print("❌ Blockchain integrity verification failed")
        
        return is_valid
    
    def verify_file(self, filename: str) -> bool:
        """Verify integrity of a specific file."""
        print(f"Verifying file: {filename}")
        
        # Get file blocks
        file_blocks = self.blockchain.get_file_blocks(filename)
        if not file_blocks:
            print(f"❌ File '{filename}' not found in blockchain")
            return False
        
        # Sort blocks by index
        file_blocks.sort(key=lambda b: b.index)
        
        # Check for tampering
        tampered_blocks = self.blockchain.detect_tampering(filename)
        if tampered_blocks:
            print(f"❌ Tampering detected in blocks: {tampered_blocks}")
            return False
        
        # Verify each chunk in IPFS
        total_chunks = len(file_blocks)
        verified_chunks = 0
        
        for i, block in enumerate(file_blocks):
            print(f"   Verifying chunk {i+1}/{total_chunks}...", end=" ")
            
            # Download chunk from IPFS
            chunk_data = self.ipfs_client.download_chunk(block.ipfs_hash)
            if chunk_data is None:
                print("❌ Failed to download from IPFS")
                continue
            
            # Verify chunk hash
            if self.ipfs_client.verify_chunk(chunk_data, block.chunk_hash):
                print("✅")
                verified_chunks += 1
            else:
                print("❌ Hash mismatch")
        
        success = verified_chunks == total_chunks
        
        if success:
            print(f"✅ File '{filename}' verified successfully")
            print(f"   Total chunks: {total_chunks}")
            print(f"   Total size: {sum(block.file_size for block in file_blocks)} bytes")
        else:
            print(f"❌ File '{filename}' verification failed")
            print(f"   Verified chunks: {verified_chunks}/{total_chunks}")
        
        fs_logger.log_verify(filename, "SUCCESS" if success else "FAILED")
        return success
    
    def list_files(self):
        """List all files in the blockchain."""
        print("Files in blockchain:")
        
        files = set()
        for block in self.blockchain.chain:
            if block.filename != "GENESIS":
                files.add(block.filename)
        
        if not files:
            print("   No files found")
            return
        
        for filename in sorted(files):
            file_blocks = self.blockchain.get_file_blocks(filename)
            total_size = sum(block.file_size for block in file_blocks)
            chunk_count = len(file_blocks)
            
            print(f"   📄 {filename}")
            print(f"      Size: {total_size} bytes")
            print(f"      Chunks: {chunk_count}")
    
    def show_blockchain_info(self):
        """Show blockchain information."""
        info = self.blockchain.get_blockchain_info()
        
        print("Blockchain Information:")
        print(f"   Total blocks: {info['total_blocks']}")
        print(f"   Is valid: {'✅' if info['is_valid'] else '❌'}")
        print(f"   Files: {len(info['files'])}")
        
        if info['latest_block_hash']:
            print(f"   Latest block hash: {info['latest_block_hash'][:16]}...")
    
    def print_blockchain(self):
        """Print the entire blockchain."""
        self.blockchain.print_blockchain()

def main():
    """Main CLI function."""
    parser = argparse.ArgumentParser(
        description="Blockchain-backed FUSE filesystem integrity checker"
    )
    
    parser.add_argument(
        'command',
        choices=['verify-blockchain', 'verify-file', 'list-files', 'info', 'print-blockchain'],
        help='Command to execute'
    )
    
    parser.add_argument(
        '--file',
        type=str,
        help='Filename for file-specific operations'
    )
    
    args = parser.parse_args()
    
    # Check IPFS connection for operations that need it
    if args.command in ['verify-file'] and not ipfs_client.is_connected():
        print("❌ Warning: IPFS daemon is not running. Using simulation mode.")
        print("For full verification, start IPFS with: ipfs daemon")
    
    checker = IntegrityChecker()
    
    try:
        if args.command == 'verify-blockchain':
            success = checker.verify_blockchain()
            sys.exit(0 if success else 1)
        
        elif args.command == 'verify-file':
            if not args.file:
                print("❌ Error: --file argument required for verify-file command")
                sys.exit(1)
            success = checker.verify_file(args.file)
            sys.exit(0 if success else 1)
        
        elif args.command == 'list-files':
            checker.list_files()
        
        elif args.command == 'info':
            checker.show_blockchain_info()
        
        elif args.command == 'print-blockchain':
            checker.print_blockchain()
    
    except KeyboardInterrupt:
        print("\\n❌ Operation cancelled by user")
        sys.exit(1)
    except Exception as e:
        print(f"❌ Error: {e}")
        sys.exit(1)

if __name__ == '__main__':
    main()
'''
    create_file('myfuse/integrity_checker.py', content)

def create_init_py():
    """Create __init__.py file."""
    content = '''"""
Blockchain-backed FUSE filesystem package.
"""

__version__ = "1.0.0"
__author__ = "Blockchain FUSE Team"
__description__ = "A secure, blockchain-backed filesystem using FUSE and IPFS"
'''
    create_file('myfuse/__init__.py', content)

def create_readme():
    """Create README.md file."""
    content = '''# Blockchain-Backed Storage Driver using FUSE and IPFS

A user-space file system implementation that combines FUSE (Filesystem in Userspace) with IPFS (InterPlanetary File System) and blockchain principles to create a secure, tamper-resistant storage system.

## 🎯 Project Overview

This project demonstrates key Operating Systems concepts including:
- **File Systems**: Custom FUSE implementation with standard operations
- **Data Integrity**: SHA-256 hashing and blockchain-like verification
- **Distributed Storage**: IPFS integration for decentralized file storage
- **Security**: Tamper detection and immutability simulation
- **Proof-of-Work**: Simple mining algorithm with configurable difficulty

## 🚀 Quick Start

1. **Install dependencies**:
   ```bash
   pip install fusepy ipfshttpclient
