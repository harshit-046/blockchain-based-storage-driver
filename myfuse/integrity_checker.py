"""
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
        """
        Verify integrity of a specific file.
        
        Args:
            filename: Name of the file to verify
            
        Returns:
            True if file is valid, False otherwise
        """
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
        print("❌ Error: IPFS daemon is not running. Please start IPFS first.")
        print("Run: ipfs daemon")
        sys.exit(1)
    
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
        print("\n❌ Operation cancelled by user")
        sys.exit(1)
    except Exception as e:
        print(f"❌ Error: {e}")
        sys.exit(1)

if __name__ == '__main__':
    main()
