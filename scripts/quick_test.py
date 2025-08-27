"""
Quick test script to verify the blockchain filesystem is working.
"""

import os
import sys
import subprocess

def quick_test():
    """Run a quick test of the blockchain filesystem."""
    print("🚀 Quick Test of Blockchain FUSE Filesystem")
    print("=" * 50)
    
    # Check if project is set up
    required_files = ['myfuse/blockchain.py', 'myfuse/ipfs_client.py', 'myfuse/config.py']
    missing_files = [f for f in required_files if not os.path.exists(f)]
    
    if missing_files:
        print(f"\n❌ Project not set up! Missing files: {missing_files}")
        print("\n🔧 SOLUTION: Run the setup script first:")
        print("   python scripts/setup_all.py")
        print("\n   This will create all necessary project files.")
        return False
    
    print("✅ Project files found, proceeding with tests...")
    
    # Test 1: Basic blockchain operations
    print("\n1️⃣  Testing Basic Blockchain Operations...")
    try:
        result = subprocess.run([
            sys.executable, '-c', '''
import sys
sys.path.append("myfuse")
from blockchain import blockchain

print(f"   📊 Blockchain has {len(blockchain.chain)} blocks")

# Add a test block
blockchain.add_block("quick_test.txt", 512, "test_hash_123", "ipfs_test_456")
print(f"   ✅ Added test block, now {len(blockchain.chain)} blocks")

# Validate
is_valid = blockchain.validate_chain()
print(f"   🔍 Blockchain valid: {is_valid}")
'''
        ], capture_output=True, text=True, timeout=15)
        
        print(result.stdout)
        if result.returncode == 0:
            print("   ✅ Basic operations: PASSED")
        else:
            print("   ❌ Basic operations: FAILED")
            print(result.stderr)
    except Exception as e:
        print(f"   ❌ Basic operations: ERROR - {e}")
    
    # Test 2: File chunking simulation
    print("\n2️⃣  Testing File Chunking...")
    try:
        result = subprocess.run([
            sys.executable, '-c', '''
import sys
sys.path.append("myfuse")
import hashlib
from ipfs_client import ipfs_client

# Test data
test_data = b"This is test data for chunking simulation."
print(f"   📄 Test data: {len(test_data)} bytes")

# Upload chunk
ipfs_hash = ipfs_client.upload_chunk(test_data)
print(f"   📤 Uploaded to IPFS: {ipfs_hash}")

# Download chunk
downloaded = ipfs_client.download_chunk(ipfs_hash)
print(f"   📥 Downloaded: {len(downloaded) if downloaded else 0} bytes")

# Verify
chunk_hash = hashlib.sha256(test_data).hexdigest()
is_valid = ipfs_client.verify_chunk(downloaded, chunk_hash) if downloaded else False
print(f"   🔍 Chunk valid: {is_valid}")
'''
        ], capture_output=True, text=True, timeout=15)
        
        print(result.stdout)
        if result.returncode == 0:
            print("   ✅ File chunking: PASSED")
        else:
            print("   ❌ File chunking: FAILED")
            print(result.stderr)
    except Exception as e:
        print(f"   ❌ File chunking: ERROR - {e}")
    
    # Test 3: Integrity verification
    print("\n3️⃣  Testing Integrity Verification...")
    try:
        result = subprocess.run([
            sys.executable, '-c', '''
import sys
sys.path.append("myfuse")
from blockchain import blockchain

# Get blockchain info
info = blockchain.get_blockchain_info()
print(f"   📊 Total blocks: {info['total_blocks']}")
print(f"   📁 Files: {len(info['files'])}")
print(f"   ✅ Valid: {info['is_valid']}")

# List files
if info['files']:
    print(f"   📋 File list: {list(info['files'])}")
else:
    print("   📋 No files in blockchain yet")
'''
        ], capture_output=True, text=True, timeout=15)
        
        print(result.stdout)
        if result.returncode == 0:
            print("   ✅ Integrity verification: PASSED")
        else:
            print("   ❌ Integrity verification: FAILED")
            print(result.stderr)
    except Exception as e:
        print(f"   ❌ Integrity verification: ERROR - {e}")
    
    # Summary
    print("\n" + "=" * 50)
    print("🎯 Quick Test Summary:")
    print("   • Blockchain operations tested")
    print("   • File chunking simulation tested")
    print("   • Integrity verification tested")
    print("\n💡 Next Steps:")
    print("   • Run full tests: python scripts/run_guide.py")
    print("   • Install FUSE: pip install fusepy")
    print("   • Mount filesystem: python myfuse/main.py ./mountpoint")
    print("   • Read documentation: cat README.md")

if __name__ == '__main__':
    quick_test()
