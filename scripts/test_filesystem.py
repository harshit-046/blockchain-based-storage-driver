"""
Comprehensive test script for the blockchain FUSE filesystem.
"""

import os
import sys
import time
import subprocess
import tempfile
import hashlib
from pathlib import Path

# Import modules directly (assuming they're in the same project)
try:
    from myfuse.blockchain import blockchain
    from myfuse.ipfs_client import ipfs_client
    from myfuse.integrity_checker import IntegrityChecker
except ImportError:
    # Alternative import method if direct import fails
    import importlib.util
    
    def load_module(name, path):
        spec = importlib.util.spec_from_file_location(name, path)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        return module
    
    # Load modules manually
    blockchain_module = load_module("blockchain", "myfuse/blockchain.py")
    ipfs_module = load_module("ipfs_client", "myfuse/ipfs_client.py")
    checker_module = load_module("integrity_checker", "myfuse/integrity_checker.py")
    
    blockchain = blockchain_module.blockchain
    ipfs_client = ipfs_module.ipfs_client
    IntegrityChecker = checker_module.IntegrityChecker

class FilesystemTester:
    """Comprehensive tester for the blockchain FUSE filesystem."""
    
    def __init__(self, mount_point="./test_mountpoint"):
        self.mount_point = mount_point
        self.test_files = []
        self.checker = IntegrityChecker()
        
    def setup(self):
        """Set up test environment."""
        print("🔧 Setting up test environment...")
        
        # Create mount point
        os.makedirs(self.mount_point, exist_ok=True)
        
        # Check IPFS connection
        if not ipfs_client.is_connected():
            print("❌ IPFS daemon not running. Please start with: ipfs daemon")
            return False
        
        print("✅ Test environment ready")
        return True
    
    def test_small_file(self):
        """Test writing and reading a small file."""
        print("\n📝 Testing small file operations...")
        
        test_content = "Hello, blockchain world! This is a test file."
        test_file = os.path.join(self.mount_point, "small_test.txt")
        
        try:
            # Write file
            with open(test_file, 'w') as f:
                f.write(test_content)
            
            # Read file back
            with open(test_file, 'r') as f:
                read_content = f.read()
            
            if read_content == test_content:
                print("✅ Small file read/write successful")
                self.test_files.append("small_test.txt")
                return True
            else:
                print("❌ Content mismatch in small file test")
                return False
                
        except Exception as e:
            print(f"❌ Small file test failed: {e}")
            return False
    
    def test_large_file(self):
        """Test writing and reading a large file (multiple chunks)."""
        print("\n📦 Testing large file operations...")
        
        # Create 5KB of test data (5 chunks)
        test_content = "A" * 1024 + "B" * 1024 + "C" * 1024 + "D" * 1024 + "E" * 1024
        test_file = os.path.join(self.mount_point, "large_test.txt")
        
        try:
            # Write file
            with open(test_file, 'w') as f:
                f.write(test_content)
            
            # Read file back
            with open(test_file, 'r') as f:
                read_content = f.read()
            
            if read_content == test_content:
                print("✅ Large file read/write successful")
                print(f"   File size: {len(test_content)} bytes")
                self.test_files.append("large_test.txt")
                return True
            else:
                print("❌ Content mismatch in large file test")
                return False
                
        except Exception as e:
            print(f"❌ Large file test failed: {e}")
            return False
    
    def test_binary_file(self):
        """Test writing and reading a binary file."""
        print("\n🔢 Testing binary file operations...")
        
        # Create binary test data
        test_data = bytes(range(256)) * 4  # 1KB of binary data
        test_file = os.path.join(self.mount_point, "binary_test.bin")
        
        try:
            # Write binary file
            with open(test_file, 'wb') as f:
                f.write(test_data)
            
            # Read binary file back
            with open(test_file, 'rb') as f:
                read_data = f.read()
            
            if read_data == test_data:
                print("✅ Binary file read/write successful")
                print(f"   File size: {len(test_data)} bytes")
                self.test_files.append("binary_test.bin")
                return True
            else:
                print("❌ Content mismatch in binary file test")
                return False
                
        except Exception as e:
            print(f"❌ Binary file test failed: {e}")
            return False
    
    def test_multiple_files(self):
        """Test writing multiple files."""
        print("\n📚 Testing multiple file operations...")
        
        files_created = 0
        
        for i in range(3):
            filename = f"multi_test_{i}.txt"
            content = f"This is test file number {i}\n" * (i + 1)
            test_file = os.path.join(self.mount_point, filename)
            
            try:
                with open(test_file, 'w') as f:
                    f.write(content)
                
                # Verify immediately
                with open(test_file, 'r') as f:
                    read_content = f.read()
                
                if read_content == content:
                    files_created += 1
                    self.test_files.append(filename)
                
            except Exception as e:
                print(f"❌ Failed to create {filename}: {e}")
        
        if files_created == 3:
            print("✅ Multiple files created successfully")
            return True
        else:
            print(f"❌ Only {files_created}/3 files created successfully")
            return False
    
    def test_file_listing(self):
        """Test directory listing functionality."""
        print("\n📋 Testing file listing...")
        
        try:
            files = os.listdir(self.mount_point)
            expected_files = set(self.test_files)
            actual_files = set(files)
            
            if expected_files.issubset(actual_files):
                print("✅ File listing successful")
                print(f"   Files found: {sorted(files)}")
                return True
            else:
                missing = expected_files - actual_files
                print(f"❌ Missing files in listing: {missing}")
                return False
                
        except Exception as e:
            print(f"❌ File listing failed: {e}")
            return False
    
    def test_blockchain_integrity(self):
        """Test blockchain integrity verification."""
        print("\n🔗 Testing blockchain integrity...")
        
        try:
            is_valid = self.checker.verify_blockchain()
            
            if is_valid:
                print("✅ Blockchain integrity verified")
                return True
            else:
                print("❌ Blockchain integrity check failed")
                return False
                
        except Exception as e:
            print(f"❌ Blockchain integrity test failed: {e}")
            return False
    
    def test_file_verification(self):
        """Test individual file verification."""
        print("\n🔍 Testing file verification...")
        
        verified_files = 0
        
        for filename in self.test_files:
            try:
                is_valid = self.checker.verify_file(filename)
                if is_valid:
                    verified_files += 1
                    print(f"   ✅ {filename} verified")
                else:
                    print(f"   ❌ {filename} verification failed")
                    
            except Exception as e:
                print(f"   ❌ {filename} verification error: {e}")
        
        if verified_files == len(self.test_files):
            print("✅ All files verified successfully")
            return True
        else:
            print(f"❌ Only {verified_files}/{len(self.test_files)} files verified")
            return False
    
    def test_immutability(self):
        """Test filesystem immutability (should fail to modify files)."""
        print("\n🔒 Testing immutability...")
        
        if not self.test_files:
            print("❌ No test files available for immutability test")
            return False
        
        test_file = os.path.join(self.mount_point, self.test_files[0])
        
        try:
            # Try to truncate file (should fail)
            with open(test_file, 'w') as f:
                f.write("This should not work")
            
            print("❌ File modification succeeded (immutability broken)")
            return False
            
        except Exception as e:
            print("✅ File modification properly blocked (immutability working)")
            return True
    
    def run_all_tests(self):
        """Run all tests and report results."""
        print("🧪 Starting Blockchain FUSE Filesystem Tests")
        print("=" * 60)
        
        if not self.setup():
            return False
        
        tests = [
            ("Small File Operations", self.test_small_file),
            ("Large File Operations", self.test_large_file),
            ("Binary File Operations", self.test_binary_file),
            ("Multiple Files", self.test_multiple_files),
            ("File Listing", self.test_file_listing),
            ("Blockchain Integrity", self.test_blockchain_integrity),
            ("File Verification", self.test_file_verification),
            ("Immutability", self.test_immutability),
        ]
        
        passed = 0
        total = len(tests)
        
        for test_name, test_func in tests:
            try:
                if test_func():
                    passed += 1
            except Exception as e:
                print(f"❌ {test_name} crashed: {e}")
        
        print("\n" + "=" * 60)
        print(f"📊 Test Results: {passed}/{total} tests passed")
        
        if passed == total:
            print("🎉 All tests passed! Filesystem is working correctly.")
        else:
            print("⚠️  Some tests failed. Check the output above for details.")
        
        return passed == total
    
    def cleanup(self):
        """Clean up test environment."""
        print("\n🧹 Cleaning up test environment...")
        
        # Remove test files from mount point
        for filename in self.test_files:
            test_file = os.path.join(self.mount_point, filename)
            try:
                if os.path.exists(test_file):
                    os.remove(test_file)
            except:
                pass  # Files might be immutable
        
        print("✅ Cleanup completed")

def main():
    """Main test function."""
    import argparse
    
    parser = argparse.ArgumentParser(description="Test the blockchain FUSE filesystem")
    parser.add_argument(
        '--mount-point',
        default='./test_mountpoint',
        help='Mount point for testing (default: ./test_mountpoint)'
    )
    parser.add_argument(
        '--cleanup',
        action='store_true',
        help='Clean up after tests'
    )
    
    args = parser.parse_args()
    
    tester = FilesystemTester(args.mount_point)
    
    try:
        success = tester.run_all_tests()
        
        if args.cleanup:
            tester.cleanup()
        
        sys.exit(0 if success else 1)
        
    except KeyboardInterrupt:
        print("\n❌ Tests interrupted by user")
        if args.cleanup:
            tester.cleanup()
        sys.exit(1)

if __name__ == '__main__':
    main()
