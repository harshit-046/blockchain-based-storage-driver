"""
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
