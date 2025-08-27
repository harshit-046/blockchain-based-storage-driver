"""
Main FUSE filesystem implementation for blockchain-backed storage.
"""

import os
import sys
import errno
import hashlib
from typing import Dict, List, Optional
from fuse import FUSE, FuseOSError, Operations
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
            latest_block = max(file_blocks, key=lambda b: b.index)
            
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
            # Each write operation creates a new version of the file
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
    if len(sys.argv) != 2:
        print(f"Usage: {sys.argv[0]} <mountpoint>")
        sys.exit(1)
    
    mountpoint = sys.argv[1]
    
    # Check if IPFS is running
    if not ipfs_client.is_connected():
        print("Error: IPFS daemon is not running. Please start IPFS first.")
        print("Run: ipfs daemon")
        sys.exit(1)
    
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
        print(f"\nFilesystem unmounted from {mountpoint}")
    except Exception as e:
        fs_logger.log_error("MOUNT", str(e))
        print(f"Error mounting filesystem: {e}")
        sys.exit(1)

if __name__ == '__main__':
    main()
