"""
Complete guide for testing and running the blockchain FUSE filesystem.
This script provides step-by-step instructions and automated testing.
"""

import os
import sys
import subprocess
import time
import signal

def print_header(title):
    """Print a formatted header."""
    print(f"\n{'='*60}")
    print(f"  {title}")
    print(f"{'='*60}")

def print_step(step_num, title, description=""):
    """Print a formatted step."""
    print(f"\n🔹 Step {step_num}: {title}")
    if description:
        print(f"   {description}")
    print("-" * 40)

def check_setup():
    """Check if the project is properly set up."""
    print("🔍 Checking project setup...")
    
    required_files = [
        'myfuse/config.py',
        'myfuse/blockchain.py',
        'myfuse/log.py'
    ]
    
    missing_files = []
    for file_path in required_files:
        if not os.path.exists(file_path):
            missing_files.append(file_path)
    
    if missing_files:
        print(f"❌ Missing files: {missing_files}")
        print("💡 Run setup first: python scripts/setup_all.py")
        return False
    
    print("✅ Project setup looks good!")
    return True

def test_basic_components():
    """Test basic blockchain components."""
    print_step(1, "Testing Basic Components", "Testing blockchain creation and validation")
    
    try:
        # Test blockchain creation
        print("   Creating test blockchain...")
        result = subprocess.run([
            sys.executable, '-c', '''
import sys
sys.path.append("myfuse")
from blockchain import Blockchain

# Create test blockchain
bc = Blockchain("test_chain.json")
print(f"✅ Blockchain created with {len(bc.chain)} blocks")

# Add test block
bc.add_block("test.txt", 1024, "abc123", "ipfs_hash_123")
print(f"✅ Added block, now have {len(bc.chain)} blocks")

# Validate chain
is_valid = bc.validate_chain()
print(f"✅ Blockchain validation: {'PASSED' if is_valid else 'FAILED'}")

# Clean up
import os
if os.path.exists("test_chain.json"):
    os.remove("test_chain.json")
print("✅ Test completed successfully")
'''
        ], capture_output=True, text=True, timeout=30)
        
        print(result.stdout)
        if result.stderr:
            print(f"   ⚠️  Warnings: {result.stderr}")
        
        return result.returncode == 0
        
    except Exception as e:
        print(f"   ❌ Component test failed: {e}")
        return False

def test_file_operations():
    """Test file operations without FUSE."""
    print_step(2, "Testing File Operations", "Testing file chunking and blockchain storage")
    
    try:
        print("   Testing file chunking and storage...")
        result = subprocess.run([
            sys.executable, '-c', '''
import sys
sys.path.append("myfuse")
import hashlib
from blockchain import blockchain
from ipfs_client import ipfs_client

# Test data
test_data = b"Hello, blockchain world! This is a test file for chunking."
chunk_size = 32  # Small chunks for testing

print(f"📄 Test data: {len(test_data)} bytes")

# Split into chunks
chunks = []
for i in range(0, len(test_data), chunk_size):
    chunk = test_data[i:i + chunk_size]
    chunks.append(chunk)

print(f"📦 Split into {len(chunks)} chunks")

# Process each chunk
filename = "test_file.txt"
for i, chunk in enumerate(chunks):
    chunk_hash = hashlib.sha256(chunk).hexdigest()
    ipfs_hash = ipfs_client.upload_chunk(chunk)
    
    # Add to blockchain
    block = blockchain.add_block(filename, len(chunk), chunk_hash, ipfs_hash)
    print(f"   ✅ Chunk {i+1}: {len(chunk)} bytes -> Block {block.index}")

# Verify file blocks
file_blocks = blockchain.get_file_blocks(filename)
print(f"📋 File has {len(file_blocks)} blocks in blockchain")

# Test reconstruction
reconstructed = b""
for block in sorted(file_blocks, key=lambda b: b.index):
    chunk_data = ipfs_client.download_chunk(block.ipfs_hash)
    if chunk_data and ipfs_client.verify_chunk(chunk_data, block.chunk_hash):
        reconstructed += chunk_data
        print(f"   ✅ Chunk {block.index} verified and reconstructed")
    else:
        print(f"   ❌ Chunk {block.index} verification failed")

# Verify reconstruction
if reconstructed == test_data:
    print("🎉 File reconstruction successful!")
else:
    print("❌ File reconstruction failed!")
    print(f"   Original: {test_data}")
    print(f"   Reconstructed: {reconstructed}")
'''
        ], capture_output=True, text=True, timeout=30)
        
        print(result.stdout)
        if result.stderr:
            print(f"   ⚠️  Warnings: {result.stderr}")
        
        return result.returncode == 0
        
    except Exception as e:
        print(f"   ❌ File operations test failed: {e}")
        return False

def test_integrity_verification():
    """Test blockchain integrity verification."""
    print_step(3, "Testing Integrity Verification", "Testing tamper detection and verification")
    
    try:
        print("   Testing blockchain integrity...")
        result = subprocess.run([
            sys.executable, '-c', '''
import sys
sys.path.append("myfuse")
from blockchain import blockchain

# Check current blockchain
print(f"📊 Current blockchain: {len(blockchain.chain)} blocks")

# Validate blockchain
is_valid = blockchain.validate_chain()
print(f"🔍 Blockchain validation: {'✅ VALID' if is_valid else '❌ INVALID'}")

# Get blockchain info
info = blockchain.get_blockchain_info()
print(f"📈 Blockchain info:")
print(f"   Total blocks: {info['total_blocks']}")
print(f"   Files: {len(info['files'])}")
print(f"   Valid: {info['is_valid']}")

# List files
files = set()
for block in blockchain.chain:
    if block.filename != "GENESIS":
        files.add(block.filename)

if files:
    print(f"📁 Files in blockchain: {list(files)}")
    
    # Test tampering detection for each file
    for filename in files:
        tampered = blockchain.detect_tampering(filename)
        if tampered:
            print(f"   ⚠️  {filename}: Tampering detected in blocks {tampered}")
        else:
            print(f"   ✅ {filename}: No tampering detected")
else:
    print("📁 No files in blockchain yet")

print("🎉 Integrity verification completed!")
'''
        ], capture_output=True, text=True, timeout=30)
        
        print(result.stdout)
        if result.stderr:
            print(f"   ⚠️  Warnings: {result.stderr}")
        
        return result.returncode == 0
        
    except Exception as e:
        print(f"   ❌ Integrity verification test failed: {e}")
        return False

def show_manual_testing_guide():
    """Show manual testing instructions."""
    print_step(4, "Manual Testing Guide", "Step-by-step manual testing instructions")
    
    print("""
🎯 MANUAL TESTING STEPS:

1️⃣  BASIC BLOCKCHAIN OPERATIONS:
   python -c "
   import sys; sys.path.append('myfuse')
   from blockchain import blockchain
   print('Blocks:', len(blockchain.chain))
   blockchain.print_blockchain()
   "

2️⃣  ADD TEST DATA:
   python -c "
   import sys; sys.path.append('myfuse')
   from blockchain import blockchain
   blockchain.add_block('manual_test.txt', 1024, 'hash123', 'ipfs456')
   print('Added test block')
   "

3️⃣  VERIFY BLOCKCHAIN:
   python -c "
   import sys; sys.path.append('myfuse')
   from blockchain import blockchain
   print('Valid:', blockchain.validate_chain())
   "

4️⃣  LIST FILES:
   python -c "
   import sys; sys.path.append('myfuse')
   from blockchain import blockchain
   files = set(b.filename for b in blockchain.chain if b.filename != 'GENESIS')
   print('Files:', list(files))
   "

5️⃣  VIEW LOGS:
   cat logs.txt

6️⃣  VIEW BLOCKCHAIN DATA:
   cat blockchain.json | python -m json.tool
""")

def show_fuse_testing_guide():
    """Show FUSE filesystem testing guide."""
    print_step(5, "FUSE Filesystem Testing", "Testing the full filesystem (requires fusepy)")
    
    print("""
🔧 FUSE FILESYSTEM TESTING:

📋 PREREQUISITES:
   • Install FUSE: pip install fusepy
   • (Optional) Install IPFS: https://ipfs.io/
   • (Optional) Start IPFS: ipfs daemon

🚀 START FILESYSTEM:
   Terminal 1: python myfuse/main.py ./mountpoint
   (Keep this running)

📝 TEST FILE OPERATIONS:
   Terminal 2:
   echo "Hello blockchain!" > ./mountpoint/test1.txt
   echo "Second file" > ./mountpoint/test2.txt
   cat ./mountpoint/test1.txt
   ls -la ./mountpoint/

🔍 VERIFY INTEGRITY:
   python myfuse/integrity_checker.py verify-blockchain
   python myfuse/integrity_checker.py verify-file --file test1.txt
   python myfuse/integrity_checker.py list-files
   python myfuse/integrity_checker.py info

🛑 STOP FILESYSTEM:
   Press Ctrl+C in Terminal 1
""")

def show_advanced_testing():
    """Show advanced testing scenarios."""
    print_step(6, "Advanced Testing", "Performance and edge case testing")
    
    print("""
🚀 ADVANCED TESTING SCENARIOS:

📊 PERFORMANCE TESTING:
   # Large file test
   dd if=/dev/zero of=./mountpoint/large.bin bs=1024 count=100
   
   # Multiple files test
   for i in {1..10}; do
     echo "File $i content" > ./mountpoint/file_$i.txt
   done
   
   # Time operations
   time cat ./mountpoint/large.bin > /dev/null

🔒 SECURITY TESTING:
   # Test immutability
   echo "original" > ./mountpoint/immutable.txt
   echo "modified" > ./mountpoint/immutable.txt  # Should fail or create new version
   
   # Test tampering detection
   python -c "
   import sys; sys.path.append('myfuse')
   from blockchain import blockchain
   # Manually corrupt a block hash
   if len(blockchain.chain) > 1:
       blockchain.chain[1].hash = 'corrupted_hash'
       print('Corrupted block hash')
   print('Valid:', blockchain.validate_chain())
   "

🧪 EDGE CASES:
   # Empty file
   touch ./mountpoint/empty.txt
   
   # Binary file
   dd if=/dev/urandom of=./mountpoint/binary.bin bs=512 count=1
   
   # Special characters in filename
   echo "special" > "./mountpoint/file with spaces.txt"

📈 MONITORING:
   # Watch logs in real-time
   tail -f logs.txt
   
   # Monitor blockchain growth
   watch -n 1 'wc -l blockchain.json'
   
   # Check system resources
   top -p $(pgrep -f "python.*main.py")
""")

def run_comprehensive_test():
    """Run comprehensive automated tests."""
    print_header("COMPREHENSIVE AUTOMATED TESTING")
    
    if not check_setup():
        return False
    
    tests = [
        ("Basic Components", test_basic_components),
        ("File Operations", test_file_operations),
        ("Integrity Verification", test_integrity_verification),
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        try:
            if test_func():
                passed += 1
                print(f"✅ {test_name}: PASSED")
            else:
                print(f"❌ {test_name}: FAILED")
        except Exception as e:
            print(f"💥 {test_name}: CRASHED - {e}")
    
    print(f"\n📊 Test Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All automated tests passed!")
        return True
    else:
        print("⚠️  Some tests failed - check output above")
        return False

def main():
    """Main function."""
    print_header("BLOCKCHAIN FUSE FILESYSTEM - TESTING & RUNNING GUIDE")
    
    print("""
This guide will help you test and run the blockchain FUSE filesystem project.
Choose from the following options:

🧪 AUTOMATED TESTING:
   • Runs comprehensive automated tests
   • Tests blockchain, file operations, and integrity
   • No manual intervention required

📋 MANUAL TESTING:
   • Step-by-step manual testing instructions
   • Interactive blockchain operations
   • Full control over testing process

🔧 FUSE FILESYSTEM:
   • Full filesystem testing with FUSE
   • Real file operations through mount point
   • Requires fusepy installation

🚀 ADVANCED TESTING:
   • Performance and security testing
   • Edge cases and stress testing
   • Monitoring and debugging
""")
    
    while True:
        print("\n" + "="*40)
        print("Choose an option:")
        print("1. Run Automated Tests")
        print("2. Show Manual Testing Guide")
        print("3. Show FUSE Filesystem Guide")
        print("4. Show Advanced Testing Guide")
        print("5. Run All Guides")
        print("0. Exit")
        
        try:
            choice = input("\nEnter your choice (0-5): ").strip()
            
            if choice == '0':
                print("👋 Goodbye!")
                break
            elif choice == '1':
                run_comprehensive_test()
            elif choice == '2':
                show_manual_testing_guide()
            elif choice == '3':
                show_fuse_testing_guide()
            elif choice == '4':
                show_advanced_testing()
            elif choice == '5':
                run_comprehensive_test()
                show_manual_testing_guide()
                show_fuse_testing_guide()
                show_advanced_testing()
            else:
                print("❌ Invalid choice. Please enter 0-5.")
                
        except KeyboardInterrupt:
            print("\n👋 Goodbye!")
            break
        except Exception as e:
            print(f"❌ Error: {e}")

if __name__ == '__main__':
    main()
