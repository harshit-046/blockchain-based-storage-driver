# Blockchain-Backed Storage Driver using FUSE and IPFS

A user-space file system implementation that combines FUSE (Filesystem in Userspace) with IPFS (InterPlanetary File System) and blockchain principles to create a secure, tamper-resistant storage system.

## 🎯 Project Overview

This project demonstrates key Operating Systems concepts including:

* **File Systems**: Custom FUSE implementation with standard operations
* **Data Integrity**: SHA-256 hashing and blockchain-like verification
* **Distributed Storage**: IPFS integration for decentralized file storage
* **Security**: Tamper detection and immutability simulation
* **Proof-of-Work**: Simple mining algorithm with configurable difficulty

## 🏗️ Architecture

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   User Space    │    │   FUSE Layer    │    │  Kernel Space   │
│                 │    │                 │    │                 │
│  Applications   │◄──►│  BlockchainFUSE │◄──►│  VFS Interface  │
│                 │    │                 │    │                 │
└─────────────────┘    └─────────────────┘    └─────────────────┘
         │                       │
         ▼                       ▼
┌─────────────────┐    ┌─────────────────┐
│   IPFS Client   │    │   Blockchain    │
│                 │    │                 │
│ • Upload chunks │    │ • Hash chaining │
│ • Download data │    │ • Proof-of-Work │
│ • Verify hashes │    │ • Tamper detect │
└─────────────────┘    └─────────────────┘
```

## 📦 Dependencies

Install the required Python packages:

```bash
pip install fusepy ipfshttpclient
```

> ⚠️ On Debian-based systems, if you encounter a `externally-managed-environment` error, try:
>
> ```bash
> pip install fusepy ipfshttpclient --break-system-packages
> ```
>
> or use a virtual environment with `python3 -m venv venv`.

### System Requirements

* **Python 3.10+**
* **FUSE**: Install system FUSE library

  * Ubuntu/Debian: `sudo apt-get install fuse libfuse-dev`
  * macOS: `brew install macfuse`
* **IPFS**: Install and run IPFS daemon

  * Download from: [https://ipfs.io/](https://ipfs.io/)
  * Initialize: `ipfs init`
  * Start daemon: `ipfs daemon`

## 🚀 Installation & Setup

1. **Clone/Download the project**:

   ```bash
   mkdir blockchain-fuse-storage
   cd blockchain-fuse-storage
   # Copy all project files here
   ```

2. **Install dependencies**:

   ```bash
   pip install fusepy ipfshttpclient
   ```

3. **Start IPFS daemon**:

   ```bash
   ipfs daemon
   ```

   Keep this running in a separate terminal.

4. **Create mount point**:

   ```bash
   mkdir mountpoint
   ```

## 🎮 Usage

### 1. Mount the Filesystem

```bash
python main.py ./mountpoint
```

The filesystem will be mounted at `./mountpoint`. You'll see:

```bash
Mounting blockchain-backed filesystem at ./mountpoint
Press Ctrl+C to unmount
```

> ❗ If you see an error like `mountpoint is not empty`, either empty the directory or pass the `--nonempty` mount option in your code.
>
> ❗ If you see `option allow_other only allowed if 'user_allow_other' is set`, then uncomment `user_allow_other` in `/etc/fuse.conf` and log out and back in to apply group membership changes.

### 2. Use the Filesystem

Open a new terminal and interact with the mounted filesystem:

```bash
# Write a file (will be chunked and stored in IPFS + blockchain)
echo "Hello, blockchain world!" > ./mountpoint/test.txt

# Read the file (reconstructed from IPFS chunks)
cat ./mountpoint/test.txt

# List files
ls -la ./mountpoint/

# Copy larger files
cp /path/to/large/file.pdf ./mountpoint/document.pdf
```

### 3. Verify Integrity

Use the integrity checker CLI:

```bash
# Verify entire blockchain
python integrity_checker.py verify-blockchain

# Verify specific file
python integrity_checker.py verify-file --file test.txt

# List all files in blockchain
python integrity_checker.py list-files

# Show blockchain information
python integrity_checker.py info

# Print entire blockchain
python integrity_checker.py print-blockchain
```

> 🛡️ If you manually modify `blockchain.json`, the next integrity check will show a "❌ Blockchain integrity verification failed" message for the affected block.

### 4. Unmount

Press `Ctrl+C` in the terminal running the filesystem to unmount.

## 🔧 Configuration

Edit `config.py` to customize:

```python
# IPFS settings
IPFS_HOST = 'localhost'
IPFS_PORT = 5001

# Chunk size (1KB default)
CHUNK_SIZE = 1024

# Proof-of-Work difficulty (3 leading zeros)
DIFFICULTY = 3

# File paths
BLOCKCHAIN_FILE = './blockchain.json'
LOG_FILE = './logs.txt'
```

## 📋 Test Cases

### Basic Functionality Test

```bash
# 1. Mount filesystem
python main.py ./mountpoint &

# 2. Create test file
echo "Test data for blockchain storage" > ./mountpoint/test1.txt

# 3. Verify file was stored
python integrity_checker.py verify-file --file test1.txt

# 4. Read file back
cat ./mountpoint/test1.txt

# 5. Check blockchain
python integrity_checker.py info
```

### Large File Test

```bash
# Create a larger file (multiple chunks)
dd if=/dev/urandom of=./mountpoint/large.bin bs=1024 count=10

# Verify chunking worked
python integrity_checker.py verify-file --file large.bin
python integrity_checker.py list-files
```

### Integrity Test

```bash
# Verify blockchain integrity
python integrity_checker.py verify-blockchain

# Print blockchain contents
python integrity_checker.py print-blockchain
```

## 🔍 How It Works

### File Write Process

1. **Chunking**: File is split into 1KB chunks
2. **Hashing**: Each chunk gets SHA-256 hash
3. **IPFS Upload**: Chunks uploaded to IPFS
4. **Blockchain**: New block created with:

   * Chunk hash (SHA-256)
   * IPFS hash (content address)
   * Previous block hash (chaining)
   * Proof-of-Work nonce
   * Metadata (filename, size, timestamp)

### File Read Process

1. **Block Retrieval**: Get all blocks for file from blockchain
2. **Tampering Check**: Verify block hash integrity
3. **IPFS Download**: Fetch chunks using IPFS hashes
4. **Verification**: Verify each chunk's SHA-256 hash
5. **Reconstruction**: Combine chunks to rebuild original file

### Security Features

* **Immutability**: Files cannot be modified or deleted
* **Tamper Detection**: Any blockchain modification is detected
* **Integrity Verification**: Each chunk verified before use
* **Proof-of-Work**: Prevents easy blockchain manipulation
* **Hash Chaining**: Links blocks cryptographically

## 📁 File Structure

```
myfuse/
├── main.py              # FUSE filesystem implementation
├── blockchain.py        # Blockchain logic and Block class
├── ipfs_client.py       # IPFS upload/download client
├── integrity_checker.py # CLI verification utility
├── log.py               # Logging system
├── config.py            # Configuration settings
├── README.md            # This file
├── blockchain.json      # Blockchain database (auto-created)
├── logs.txt             # System logs (auto-created)
└── mountpoint/          # Mount directory (auto-created)
```

## 🎓 Educational Value

This project teaches:

1. **Operating Systems**:

   * File system implementation
   * User-space vs kernel-space
   * FUSE architecture
   * File operations (read, write, getattr, etc.)

2. **Distributed Systems**:

   * Content-addressed storage (IPFS)
   * Decentralized file storage
   * Network protocols

3. **Cryptography & Security**:

   * Hash functions (SHA-256)
   * Blockchain principles
   * Proof-of-Work algorithms
   * Tamper detection

4. **Software Engineering**:

   * Modular design
   * Error handling
   * Logging and monitoring
   * CLI interfaces

## ⚠️ Limitations

* **Performance**: Not optimized for production use
* **Concurrency**: Single-threaded operations
* **Persistence**: Blockchain stored locally (not distributed)
* **IPFS Dependency**: Requires running IPFS daemon
* **Immutability**: Files cannot be modified (by design)

## 🐛 Troubleshooting

### IPFS Connection Issues

```bash
# Check if IPFS is running
ipfs id

# Restart IPFS daemon
ipfs daemon
```

### Mount Issues

```bash
# Check if mount point is busy
fusermount -u ./mountpoint

# Check FUSE permissions
sudo usermod -a -G fuse $USER
# Log out and log back in after running the above command
```

### Permission Errors

```bash
# Ensure proper permissions
chmod +x main.py integrity_checker.py
```

## 📚 Further Reading

* [FUSE Documentation](https://www.kernel.org/doc/html/latest/filesystems/fuse.html)
* [IPFS Documentation](https://docs.ipfs.io/)
* [Blockchain Fundamentals](https://bitcoin.org/bitcoin.pdf)
* [File System Design](https://pages.cs.wisc.edu/~remzi/OSTEP/file-intro.pdf)

## 🤝 Contributing

This is an educational project. Feel free to:

* Add new features (encryption, compression)
* Improve performance
* Add more comprehensive tests
* Enhance documentation

---

**Note**: This implementation is for educational purposes and demonstrates OS concepts in a safe, user-space environment without requiring kernel modifications.
\`\`\`
\`\`\`

```python file="scripts/setup_environment.py"
"""
Setup script to prepare the environment for the blockchain FUSE filesystem.
"""

import os
import subprocess
import sys
import json

def check_python_version():
    """Check if Python version is 3.10+"""
    if sys.version_info &lt; (3, 10):
        print("❌ Python 3.10+ required")
        return False
    print("✅ Python version check passed")
    return True

def install_dependencies():
    """Install required Python packages"""
    packages = ['fusepy', 'ipfshttpclient']
    
    for package in packages:
        try:
            print(f"Installing {package}...")
            subprocess.check_call([sys.executable, '-m', 'pip', 'install', package])
            print(f"✅ {package} installed successfully")
        except subprocess.CalledProcessError:
            print(f"❌ Failed to install {package}")
            return False
    
    return True

def check_ipfs():
    """Check if IPFS is installed and accessible"""
    try:
        result = subprocess.run(['ipfs', 'version'], capture_output=True, text=True)
        if result.returncode == 0:
            print(f"✅ IPFS found: {result.stdout.strip()}")
            return True
    except FileNotFoundError:
        pass
    
    print("❌ IPFS not found. Please install IPFS:")
    print("   Visit: https://ipfs.io/")
    print("   Or run: curl -sSL https://get.ipfs.io | sh")
    return False

def check_fuse():
    """Check if FUSE is available"""
    try:
        import fuse
        print("✅ FUSE Python bindings available")
        return True
    except ImportError:
        print("❌ FUSE Python bindings not found")
        print("   Install with: pip install fusepy")
        return False

def create_directories():
    """Create necessary directories"""
    directories = ['mountpoint', 'logs']
    
    for directory in directories:
        os.makedirs(directory, exist_ok=True)
        print(f"✅ Created directory: {directory}")

def initialize_blockchain():
    """Initialize empty blockchain file"""
    blockchain_file = 'blockchain.json'
    
    if not os.path.exists(blockchain_file):
        initial_blockchain = {
            'chain': [],
            'length': 0
        }
        
        with open(blockchain_file, 'w') as f:
            json.dump(initial_blockchain, f, indent=2)
        
        print(f"✅ Initialized blockchain file: {blockchain_file}")
    else:
        print(f"✅ Blockchain file already exists: {blockchain_file}")

def main():
    """Main setup function"""
    print("🔧 Setting up Blockchain-backed FUSE Filesystem Environment")
    print("=" * 60)
    
    checks = [
        ("Python Version", check_python_version),
        ("Dependencies", install_dependencies),
        ("IPFS", check_ipfs),
        ("FUSE", check_fuse),
    ]
    
    all_passed = True
    
    for name, check_func in checks:
        print(f"\n📋 Checking {name}...")
        if not check_func():
            all_passed = False
    
    print(f"\n📁 Creating directories...")
    create_directories()
    
    print(f"\n🔗 Initializing blockchain...")
    initialize_blockchain()
    
    print("\n" + "=" * 60)
    
    if all_passed:
        print("✅ Environment setup completed successfully!")
        print("\n🚀 Next steps:")
        print("1. Start IPFS daemon: ipfs daemon")
        print("2. Mount filesystem: python main.py ./mountpoint")
        print("3. Test with: echo 'Hello' > ./mountpoint/test.txt")
        print("4. Verify with: python integrity_checker.py verify-file --file test.txt")
    else:
        print("❌ Environment setup incomplete. Please fix the issues above.")
        sys.exit(1)

if __name__ == '__main__':
    main()
