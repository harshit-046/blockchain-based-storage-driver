"""
IPFS client for uploading and downloading file chunks.
"""

import ipfshttpclient
import hashlib
from typing import Optional
from config import IPFS_API_URL
from log import fs_logger

class IPFSClient:
    """Client for interacting with IPFS."""
    
    def __init__(self, api_url: str = IPFS_API_URL):
        """Initialize IPFS client."""
        self.api_url = api_url
        self.client = None
        self.connect()
    
    def connect(self) -> bool:
        """Connect to IPFS daemon."""
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
        """
        Upload a chunk to IPFS and return the hash.
        
        Args:
            chunk_data: The chunk data to upload
            
        Returns:
            IPFS hash of the uploaded chunk or None if failed
        """
        try:
            if not self.client:
                if not self.connect():
                    return None
            
            # Upload chunk to IPFS
            result = self.client.add_bytes(chunk_data)
            ipfs_hash = result
            
            fs_logger.log_blockchain_operation("IPFS_UPLOAD", f"Chunk uploaded: {ipfs_hash}")
            return ipfs_hash
            
        except Exception as e:
            fs_logger.log_error("IPFS_UPLOAD", str(e))
            return None
    
    def download_chunk(self, ipfs_hash: str) -> Optional[bytes]:
        """
        Download a chunk from IPFS using its hash.
        
        Args:
            ipfs_hash: The IPFS hash of the chunk
            
        Returns:
            Chunk data or None if failed
        """
        try:
            if not self.client:
                if not self.connect():
                    return None
            
            # Download chunk from IPFS
            chunk_data = self.client.cat(ipfs_hash)
            
            fs_logger.log_blockchain_operation("IPFS_DOWNLOAD", f"Chunk downloaded: {ipfs_hash}")
            return chunk_data
            
        except Exception as e:
            fs_logger.log_error("IPFS_DOWNLOAD", str(e))
            return None
    
    def verify_chunk(self, chunk_data: bytes, expected_hash: str) -> bool:
        """
        Verify chunk integrity by comparing SHA-256 hashes.
        
        Args:
            chunk_data: The chunk data to verify
            expected_hash: Expected SHA-256 hash
            
        Returns:
            True if chunk is valid, False otherwise
        """
        actual_hash = hashlib.sha256(chunk_data).hexdigest()
        return actual_hash == expected_hash
    
    def is_connected(self) -> bool:
        """Check if connected to IPFS."""
        try:
            if self.client:
                self.client.version()
                return True
        except:
            pass
        return False

# Global IPFS client instance
ipfs_client = IPFSClient()
