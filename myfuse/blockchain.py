"""
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
        """
        Perform proof of work to find a valid nonce.
        
        Args:
            block: Block to mine
            
        Returns:
            Valid nonce value
        """
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
        """
        Add a new block to the blockchain.
        
        Args:
            filename: Name of the file
            file_size: Size of the file chunk
            chunk_hash: SHA-256 hash of the chunk
            ipfs_hash: IPFS hash of the stored chunk
            
        Returns:
            The newly created block
        """
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
        """
        Validate the entire blockchain.
        
        Returns:
            True if chain is valid, False otherwise
        """
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
        """
        Detect tampering in blocks for a specific file.
        
        Args:
            filename: Name of the file to check
            
        Returns:
            List of tampered block indices
        """
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
        print("\n" + "="*80)
        print("BLOCKCHAIN CONTENTS")
        print("="*80)
        
        for block in self.chain:
            print(f"\nBlock {block.index}:")
            print(f"  Timestamp: {block.timestamp}")
            print(f"  Filename: {block.filename}")
            print(f"  File Size: {block.file_size}")
            print(f"  Chunk Hash: {block.chunk_hash[:16]}...")
            print(f"  IPFS Hash: {block.ipfs_hash}")
            print(f"  Previous Hash: {block.previous_hash[:16]}...")
            print(f"  Nonce: {block.nonce}")
            print(f"  Hash: {block.hash[:16]}...")
        
        print("\n" + "="*80)

# Global blockchain instance
blockchain = Blockchain()
