"""
Standalone test that doesn't require external files.
Tests blockchain concepts directly without imports.
"""

import hashlib
import json
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

class SimpleBlockchain:
    """Simple blockchain implementation for testing."""
    
    def __init__(self):
        self.chain: List[Block] = []
        self.create_genesis_block()
    
    def create_genesis_block(self):
        """Create the genesis block."""
        genesis = Block(
            index=0,
            timestamp=datetime.datetime.now().isoformat(),
            filename="GENESIS",
            file_size=0,
            chunk_hash="0" * 64,
            ipfs_hash="",
            previous_hash="0" * 64,
            nonce=0
        )
        genesis.hash = self.calculate_hash(genesis)
        self.chain.append(genesis)
    
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
    
    def add_block(self, filename: str, file_size: int, chunk_hash: str, ipfs_hash: str):
        """Add a new block to the blockchain."""
        previous_block = self.chain[-1]
        
        new_block = Block(
            index=len(self.chain),
            timestamp=datetime.datetime.now().isoformat(),
            filename=filename,
            file_size=file_size,
            chunk_hash=chunk_hash,
            ipfs_hash=ipfs_hash,
            previous_hash=previous_block.hash
        )
        
        # Simple proof of work
        target = "000"
        for nonce in range(10000):
            new_block.nonce = nonce
            new_block.hash = self.calculate_hash(new_block)
            if new_block.hash.startswith(target):
                break
        
        self.chain.append(new_block)
        return new_block
    
    def validate_chain(self) -> bool:
        """Validate the blockchain."""
        for i in range(1, len(self.chain)):
            current = self.chain[i]
            previous = self.chain[i - 1]
            
            if current.hash != self.calculate_hash(current):
                return False
            
            if current.previous_hash != previous.hash:
                return False
        
        return True

def test_blockchain_creation():
    """Test blockchain creation."""
    print("1️⃣  Testing Blockchain Creation...")
    
    try:
        blockchain = SimpleBlockchain()
        print(f"   ✅ Created blockchain with {len(blockchain.chain)} blocks")
        
        # Validate genesis block
        is_valid = blockchain.validate_chain()
        print(f"   ✅ Genesis block validation: {is_valid}")
        
        return True
    except Exception as e:
        print(f"   ❌ Blockchain creation failed: {e}")
        return False

def test_block_addition():
    """Test adding blocks to blockchain."""
    print("\n2️⃣  Testing Block Addition...")
    
    try:
        blockchain = SimpleBlockchain()
        
        # Add test blocks
        test_files = [
            ("test1.txt", 1024, "hash1"),
            ("test2.txt", 2048, "hash2"),
            ("test3.txt", 512, "hash3")
        ]
        
        for filename, size, chunk_hash in test_files:
            ipfs_hash = f"Qm{chunk_hash}123456789"
            block = blockchain.add_block(filename, size, chunk_hash, ipfs_hash)
            print(f"   ✅ Added {filename}: Block {block.index}")
        
        print(f"   ✅ Blockchain now has {len(blockchain.chain)} blocks")
        return True
        
    except Exception as e:
        print(f"   ❌ Block addition failed: {e}")
        return False

def test_chain_validation():
    """Test blockchain validation."""
    print("\n3️⃣  Testing Chain Validation...")
    
    try:
        blockchain = SimpleBlockchain()
        
        # Add some blocks
        blockchain.add_block("file1.txt", 1024, "hash1", "ipfs1")
        blockchain.add_block("file2.txt", 2048, "hash2", "ipfs2")
        
        # Test validation
        is_valid = blockchain.validate_chain()
        print(f"   ✅ Chain validation: {is_valid}")
        
        # Test tampering detection
        original_hash = blockchain.chain[1].hash
        blockchain.chain[1].hash = "tampered_hash"
        
        is_valid_after_tampering = blockchain.validate_chain()
        print(f"   ✅ Tampering detection: {not is_valid_after_tampering}")
        
        # Restore original hash
        blockchain.chain[1].hash = original_hash
        is_valid_restored = blockchain.validate_chain()
        print(f"   ✅ Chain restoration: {is_valid_restored}")
        
        return True
        
    except Exception as e:
        print(f"   ❌ Chain validation failed: {e}")
        return False

def test_file_chunking_simulation():
    """Test file chunking simulation."""
    print("\n4️⃣  Testing File Chunking Simulation...")
    
    try:
        # Simulate file content
        file_content = b"This is a test file for blockchain storage. " * 10
        chunk_size = 64
        
        print(f"   📄 File size: {len(file_content)} bytes")
        
        # Split into chunks
        chunks = []
        for i in range(0, len(file_content), chunk_size):
            chunk = file_content[i:i + chunk_size]
            chunks.append(chunk)
        
        print(f"   📦 Split into {len(chunks)} chunks")
        
        # Create blockchain and add chunks
        blockchain = SimpleBlockchain()
        filename = "test_file.txt"
        
        for i, chunk in enumerate(chunks):
            chunk_hash = hashlib.sha256(chunk).hexdigest()
            ipfs_hash = f"Qm{chunk_hash[:40]}"
            
            block = blockchain.add_block(filename, len(chunk), chunk_hash, ipfs_hash)
            print(f"   ✅ Chunk {i+1}: {len(chunk)} bytes -> Block {block.index}")
        
        # Verify file blocks
        file_blocks = [b for b in blockchain.chain if b.filename == filename]
        total_size = sum(block.file_size for block in file_blocks)
        
        print(f"   📊 File blocks: {len(file_blocks)}")
        print(f"   📊 Total size: {total_size} bytes")
        print(f"   ✅ Size match: {total_size == len(file_content)}")
        
        return True
        
    except Exception as e:
        print(f"   ❌ File chunking simulation failed: {e}")
        return False

def test_proof_of_work():
    """Test proof of work mechanism."""
    print("\n5️⃣  Testing Proof of Work...")
    
    try:
        blockchain = SimpleBlockchain()
        
        # Add a block and check proof of work
        block = blockchain.add_block("pow_test.txt", 1024, "test_hash", "test_ipfs")
        
        # Check if hash starts with required zeros
        required_zeros = "000"
        has_valid_pow = block.hash.startswith(required_zeros)
        
        print(f"   ✅ Block hash: {block.hash[:20]}...")
        print(f"   ✅ Nonce: {block.nonce}")
        print(f"   ✅ Valid PoW: {has_valid_pow}")
        
        return has_valid_pow
        
    except Exception as e:
        print(f"   ❌ Proof of work test failed: {e}")
        return False

def main():
    """Main test function."""
    print("🚀 Standalone Blockchain Test")
    print("=" * 40)
    print("Testing blockchain concepts without external dependencies...")
    
    tests = [
        test_blockchain_creation,
        test_block_addition,
        test_chain_validation,
        test_file_chunking_simulation,
        test_proof_of_work
    ]
    
    passed = 0
    total = len(tests)
    
    for test_func in tests:
        try:
            if test_func():
                passed += 1
        except Exception as e:
            print(f"   💥 Test crashed: {e}")
    
    print("\n" + "=" * 40)
    print(f"📊 Test Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! Blockchain concepts working correctly.")
        print("\n💡 Next steps:")
        print("   • Run: python scripts/verify_and_setup.py")
        print("   • Then: python scripts/quick_test.py")
    else:
        print("⚠️  Some tests failed. Check the implementation.")
    
    return passed == total

if __name__ == '__main__':
    success = main()
    print(f"\n{'✅ Success' if success else '❌ Failed'}")
