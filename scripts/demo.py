"""
Interactive demo of the blockchain FUSE filesystem.
"""

import os
import sys
import time
import subprocess

def print_demo_header(title):
    """Print demo header."""
    print(f"\n{'🎬'*20}")
    print(f"  {title}")
    print(f"{'🎬'*20}")

def demo_blockchain_basics():
    """Demo basic blockchain operations."""
    print_demo_header("BLOCKCHAIN BASICS DEMO")
    
    print("Let's explore the blockchain implementation...")
    time.sleep(2)
    
    print("\n📊 Current blockchain status:")
    subprocess.run([
        sys.executable, '-c', '''
import sys
sys.path.append("myfuse")
from blockchain import blockchain

print(f"   Blocks: {len(blockchain.chain)}")
print(f"   Valid: {blockchain.validate_chain()}")

if len(blockchain.chain) > 0:
    latest = blockchain.get_latest_block()
    print(f"   Latest block: {latest.index}")
    print(f"   Latest hash: {latest.hash[:16]}...")
'''
    ])
    
    input("\nPress Enter to continue...")

def demo_add_files():
    """Demo adding files to blockchain."""
    print_demo_header("ADDING FILES TO BLOCKCHAIN")
    
    print("Let's add some files to the blockchain...")
    time.sleep(1)
    
    files_to_add = [
        ("document.txt", 1024, "Document content hash"),
        ("image.jpg", 2048, "Image content hash"),
        ("data.csv", 512, "CSV data hash")
    ]
    
    for filename, size, description in files_to_add:
        print(f"\n📄 Adding {filename} ({size} bytes)...")
        subprocess.run([
            sys.executable, '-c', f'''
import sys
sys.path.append("myfuse")
import hashlib
from blockchain import blockchain

# Simulate file content
content = b"{description}" * 10
chunk_hash = hashlib.sha256(content).hexdigest()
ipfs_hash = f"Qm{chunk_hash[:40]}"  # Simulate IPFS hash

# Add to blockchain
block = blockchain.add_block("{filename}", {size}, chunk_hash, ipfs_hash)
print(f"   ✅ Added as block {block.index}")
print(f"   📋 Hash: {block.hash[:16]}...")
'''
        ])
        time.sleep(1)
    
    print(f"\n📊 Blockchain now has files!")
    subprocess.run([
        sys.executable, '-c', '''
import sys
sys.path.append("myfuse")
from blockchain import blockchain

files = set(b.filename for b in blockchain.chain if b.filename != "GENESIS")
print(f"   Files: {list(files)}")
print(f"   Total blocks: {len(blockchain.chain)}")
'''
    ])
    
    input("\nPress Enter to continue...")

def demo_integrity_check():
    """Demo integrity checking."""
    print_demo_header("INTEGRITY VERIFICATION DEMO")
    
    print("Let's verify the blockchain integrity...")
    time.sleep(1)
    
    subprocess.run([
        sys.executable, '-c', '''
import sys
sys.path.append("myfuse")
from blockchain import blockchain

print("🔍 Verifying blockchain...")
is_valid = blockchain.validate_chain()
print(f"   Result: {'✅ VALID' if is_valid else '❌ INVALID'}")

print("\\n🔍 Checking individual files...")
files = set(b.filename for b in blockchain.chain if b.filename != "GENESIS")
for filename in files:
    tampered = blockchain.detect_tampering(filename)
    if tampered:
        print(f"   ⚠️  {filename}: Tampering detected!")
    else:
        print(f"   ✅ {filename}: Integrity verified")
'''
    ])
    
    input("\nPress Enter to continue...")

def demo_tampering_detection():
    """Demo tampering detection."""
    print_demo_header("TAMPERING DETECTION DEMO")
    
    print("Let's simulate tampering and see how it's detected...")
    time.sleep(1)
    
    print("\n🔧 Simulating blockchain tampering...")
    subprocess.run([
        sys.executable, '-c', '''
import sys
sys.path.append("myfuse")
from blockchain import blockchain

if len(blockchain.chain) > 1:
    print("   📝 Original blockchain is valid")
    print(f"   ✅ Validation: {blockchain.validate_chain()}")
    
    # Corrupt a block
    original_hash = blockchain.chain[1].hash
    blockchain.chain[1].hash = "corrupted_hash_12345"
    
    print("\\n   🔨 Corrupting block 1...")
    print(f"   📝 Changed hash from {original_hash[:16]}... to corrupted_hash_12345")
    
    # Check validation
    print("\\n   🔍 Re-validating blockchain...")
    is_valid = blockchain.validate_chain()
    print(f"   ❌ Validation: {is_valid} (tampering detected!)")
    
    # Restore original hash
    blockchain.chain[1].hash = original_hash
    print("\\n   🔧 Restoring original hash...")
    print(f"   ✅ Validation: {blockchain.validate_chain()} (integrity restored)")
else:
    print("   ⚠️  Need more blocks for tampering demo")
'''
    ])
    
    input("\nPress Enter to continue...")

def demo_blockchain_structure():
    """Demo blockchain structure."""
    print_demo_header("BLOCKCHAIN STRUCTURE DEMO")
    
    print("Let's examine the blockchain structure...")
    time.sleep(1)
    
    subprocess.run([
        sys.executable, '-c', '''
import sys
sys.path.append("myfuse")
from blockchain import blockchain

print("📋 Blockchain Structure:")
print("=" * 40)

for i, block in enumerate(blockchain.chain[:5]):  # Show first 5 blocks
    print(f"\\nBlock {block.index}:")
    print(f"   Timestamp: {block.timestamp}")
    print(f"   Filename: {block.filename}")
    print(f"   File Size: {block.file_size}")
    print(f"   Previous Hash: {block.previous_hash[:16]}...")
    print(f"   Current Hash: {block.hash[:16]}...")
    print(f"   Nonce: {block.nonce}")

if len(blockchain.chain) > 5:
    print(f"\\n... and {len(blockchain.chain) - 5} more blocks")

print("\\n🔗 Hash Chain Verification:")
for i in range(1, min(4, len(blockchain.chain))):
    current = blockchain.chain[i]
    previous = blockchain.chain[i-1]
    linked = current.previous_hash == previous.hash
    print(f"   Block {i-1} -> Block {i}: {'✅' if linked else '❌'}")
'''
    ])
    
    input("\nPress Enter to continue...")

def show_next_steps():
    """Show next steps after demo."""
    print_demo_header("WHAT'S NEXT?")
    
    print("""
🎯 You've seen the blockchain filesystem in action! Here's what you can do next:

🔧 INSTALL FULL FILESYSTEM:
   pip install fusepy
   python myfuse/main.py ./mountpoint

📝 CREATE REAL FILES:
   echo "Hello blockchain!" > ./mountpoint/myfile.txt
   cat ./mountpoint/myfile.txt

🔍 VERIFY INTEGRITY:
   python myfuse/integrity_checker.py verify-blockchain
   python myfuse/integrity_checker.py verify-file --file myfile.txt

🚀 ADVANCED FEATURES:
   • Install IPFS for distributed storage
   • Add encryption for secure storage
   • Build a web interface for monitoring

📚 LEARN MORE:
   • Read README.md for detailed documentation
   • Explore the source code in myfuse/
   • Run comprehensive tests with scripts/run_guide.py

🎓 EDUCATIONAL VALUE:
   • Understanding blockchain principles
   • Learning file system concepts
   • Exploring distributed storage
   • Practicing cryptographic hashing
""")

def main():
    """Main demo function."""
    print_demo_header("BLOCKCHAIN FUSE FILESYSTEM DEMO")
    
    print("""
Welcome to the interactive demo of the blockchain-backed FUSE filesystem!

This demo will show you:
• How the blockchain stores file information
• How integrity verification works
• How tampering is detected
• The structure of the blockchain

Let's get started!
""")
    
    input("Press Enter to begin the demo...")
    
    # Check if setup is complete
    if not os.path.exists('myfuse/blockchain.py'):
        print("❌ Project not set up. Please run: python scripts/setup_all.py")
        return
    
    try:
        demo_blockchain_basics()
        demo_add_files()
        demo_integrity_check()
        demo_tampering_detection()
        demo_blockchain_structure()
        show_next_steps()
        
        print("\n🎉 Demo completed! Thank you for exploring the blockchain filesystem!")
        
    except KeyboardInterrupt:
        print("\n👋 Demo interrupted. Thanks for watching!")
    except Exception as e:
        print(f"\n❌ Demo error: {e}")

if __name__ == '__main__':
    main()
