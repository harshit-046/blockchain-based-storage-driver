"""
Simple test script for the blockchain FUSE filesystem.
This script tests the filesystem by creating files and verifying operations.
"""

import os
import sys
import time
import subprocess
import json

class SimpleFilesystemTester:
    """Simple tester that works with the mounted filesystem directly."""
    
    def __init__(self, mount_point="./mountpoint"):
        self.mount_point = mount_point
        self.test_files = []
        
    def check_mount_point(self):
        """Check if the mount point exists and is accessible."""
        if not os.path.exists(self.mount_point):
            print(f"❌ Mount point {self.mount_point} does not exist")
            print("   Please mount the filesystem first with: python myfuse/main.py ./mountpoint")
            return False
        
        if not os.path.isdir(self.mount_point):
            print(f"❌ {self.mount_point} is not a directory")
            return False
        
        print(f"✅ Mount point {self.mount_point} is accessible")
        return True
    
    def test_write_small_file(self):
        """Test writing a small file."""
        print("\n📝 Testing small file write...")
        
        test_content = "Hello, blockchain world! This is a test."
        test_file = os.path.join(self.mount_point, "test_small.txt")
        
        try:
            with open(test_file, 'w') as f:
                f.write(test_content)
            
            print("✅ Small file written successfully")
            self.test_files.append("test_small.txt")
            return True
            
        except Exception as e:
            print(f"❌ Failed to write small file: {e}")
            return False
    
    def test_read_small_file(self):
        """Test reading the small file back."""
        print("\n📖 Testing small file read...")
        
        test_file = os.path.join(self.mount_point, "test_small.txt")
        expected_content = "Hello, blockchain world! This is a test."
        
        try:
            with open(test_file, 'r') as f:
                content = f.read()
            
            if content == expected_content:
                print("✅ Small file read successfully")
                print(f"   Content: {content[:50]}...")
                return True
            else:
                print("❌ Content mismatch")
                print(f"   Expected: {expected_content[:50]}...")
                print(f"   Got: {content[:50]}...")
                return False
                
        except Exception as e:
            print(f"❌ Failed to read small file: {e}")
            return False
    
    def test_write_large_file(self):
        """Test writing a larger file (multiple chunks)."""
        print("\n📦 Testing large file write...")
        
        # Create 3KB of test data (3 chunks)
        test_content = "A" * 1024 + "B" * 1024 + "C" * 1024
        test_file = os.path.join(self.mount_point, "test_large.txt")
        
        try:
            with open(test_file, 'w') as f:
                f.write(test_content)
            
            print(f"✅ Large file written successfully ({len(test_content)} bytes)")
            self.test_files.append("test_large.txt")
            return True
            
        except Exception as e:
            print(f"❌ Failed to write large file: {e}")
            return False
    
    def test_read_large_file(self):
        """Test reading the large file back."""
        print("\n📖 Testing large file read...")
        
        test_file = os.path.join(self.mount_point, "test_large.txt")
        expected_content = "A" * 1024 + "B" * 1024 + "C" * 1024
        
        try:
            with open(test_file, 'r') as f:
                content = f.read()
            
            if content == expected_content and len(content) == 3072:
                print("✅ Large file read successfully")
                print(f"   Size: {len(content)} bytes")
                return True
            else:
                print("❌ Large file content mismatch")
                print(f"   Expected size: {len(expected_content)}")
                print(f"   Actual size: {len(content)}")
                return False
                
        except Exception as e:
            print(f"❌ Failed to read large file: {e}")
            return False
    
    def test_binary_file(self):
        """Test writing and reading a binary file."""
        print("\n🔢 Testing binary file operations...")
        
        # Create binary test data
        test_data = bytes(range(256)) * 2  # 512 bytes
        test_file = os.path.join(self.mount_point, "test_binary.bin")
        
        try:
            # Write binary file
            with open(test_file, 'wb') as f:
                f.write(test_data)
            
            # Read it back
            with open(test_file, 'rb') as f:
                read_data = f.read()
            
            if read_data == test_data:
                print(f"✅ Binary file operations successful ({len(test_data)} bytes)")
                self.test_files.append("test_binary.bin")
                return True
            else:
                print("❌ Binary file content mismatch")
                return False
                
        except Exception as e:
            print(f"❌ Binary file test failed: {e}")
            return False
    
    def test_directory_listing(self):
        """Test listing files in the directory."""
        print("\n📋 Testing directory listing...")
        
        try:
            files = os.listdir(self.mount_point)
            
            print(f"✅ Directory listing successful")
            print(f"   Files found: {sorted(files)}")
            
            # Check if our test files are listed
            missing_files = []
            for test_file in self.test_files:
                if test_file not in files:
                    missing_files.append(test_file)
            
            if missing_files:
                print(f"❌ Missing files in listing: {missing_files}")
                return False
            else:
                print("✅ All test files found in listing")
                return True
                
        except Exception as e:
            print(f"❌ Directory listing failed: {e}")
            return False
    
    def test_file_stats(self):
        """Test getting file statistics."""
        print("\n📊 Testing file statistics...")
        
        success_count = 0
        
        for test_file in self.test_files:
            file_path = os.path.join(self.mount_point, test_file)
            
            try:
                stat_info = os.stat(file_path)
                print(f"   📄 {test_file}:")
                print(f"      Size: {stat_info.st_size} bytes")
                print(f"      Mode: {oct(stat_info.st_mode)}")
                success_count += 1
                
            except Exception as e:
                print(f"   ❌ Failed to get stats for {test_file}: {e}")
        
        if success_count == len(self.test_files):
            print("✅ File statistics retrieved successfully")
            return True
        else:
            print(f"❌ Only {success_count}/{len(self.test_files)} files had accessible stats")
            return False
    
    def test_blockchain_verification(self):
        """Test blockchain verification using the CLI tool."""
        print("\n🔗 Testing blockchain verification...")
        
        try:
            # Run the integrity checker
            result = subprocess.run([
                sys.executable, 'myfuse/integrity_checker.py', 'verify-blockchain'
            ], capture_output=True, text=True, timeout=30)
            
            if result.returncode == 0:
                print("✅ Blockchain verification successful")
                print("   Output:", result.stdout.strip().split('\n')[-1])
                return True
            else:
                print("❌ Blockchain verification failed")
                print("   Error:", result.stderr.strip())
                return False
                
        except subprocess.TimeoutExpired:
            print("❌ Blockchain verification timed out")
            return False
        except Exception as e:
            print(f"❌ Blockchain verification error: {e}")
            return False
    
    def test_file_verification(self):
        """Test individual file verification."""
        print("\n🔍 Testing file verification...")
        
        if not self.test_files:
            print("❌ No test files to verify")
            return False
        
        # Test verification of the first file
        test_file = self.test_files[0]
        
        try:
            result = subprocess.run([
                sys.executable, 'myfuse/integrity_checker.py', 'verify-file', '--file', test_file
            ], capture_output=True, text=True, timeout=30)
            
            if result.returncode == 0:
                print(f"✅ File verification successful for {test_file}")
                return True
            else:
                print(f"❌ File verification failed for {test_file}")
                print("   Error:", result.stderr.strip())
                return False
                
        except subprocess.TimeoutExpired:
            print("❌ File verification timed out")
            return False
        except Exception as e:
            print(f"❌ File verification error: {e}")
            return False
    
    def run_all_tests(self):
        """Run all tests in sequence."""
        print("🧪 Simple Blockchain FUSE Filesystem Test")
        print("=" * 50)
        
        tests = [
            ("Mount Point Check", self.check_mount_point),
            ("Write Small File", self.test_write_small_file),
            ("Read Small File", self.test_read_small_file),
            ("Write Large File", self.test_write_large_file),
            ("Read Large File", self.test_read_large_file),
            ("Binary File Operations", self.test_binary_file),
            ("Directory Listing", self.test_directory_listing),
            ("File Statistics", self.test_file_stats),
            ("Blockchain Verification", self.test_blockchain_verification),
            ("File Verification", self.test_file_verification),
        ]
        
        passed = 0
        total = len(tests)
        
        for test_name, test_func in tests:
            try:
                print(f"\n🔄 Running: {test_name}")
                if test_func():
                    passed += 1
                else:
                    print(f"   ⚠️ {test_name} failed")
            except Exception as e:
                print(f"   💥 {test_name} crashed: {e}")
        
        print("\n" + "=" * 50)
        print(f"📊 Test Results: {passed}/{total} tests passed")
        
        if passed == total:
            print("🎉 All tests passed! Filesystem is working correctly.")
            print("\n💡 Try these manual tests:")
            print(f"   echo 'Manual test' > {self.mount_point}/manual.txt")
            print(f"   cat {self.mount_point}/manual.txt")
            print(f"   python myfuse/integrity_checker.py list-files")
        else:
            print("⚠️ Some tests failed. Check the filesystem setup.")
            print("\n🔧 Troubleshooting:")
            print("   1. Ensure IPFS daemon is running: ipfs daemon")
            print("   2. Mount the filesystem: python myfuse/main.py ./mountpoint")
            print("   3. Check logs in logs.txt for errors")
        
        return passed == total

def main():
    """Main function."""
    # Simple argument handling for execution environment
    mount_point = './mountpoint'
    
    # Check if custom mount point is provided in sys.argv
    for i, arg in enumerate(sys.argv):
        if arg == '--mount-point' and i + 1 < len(sys.argv):
            mount_point = sys.argv[i + 1]
            break
    
    print(f"Using mount point: {mount_point}")
    
    tester = SimpleFilesystemTester(mount_point)
    
    try:
        success = tester.run_all_tests()
        return success
        
    except KeyboardInterrupt:
        print("\n❌ Tests interrupted by user")
        return False

# Run the test directly when imported/executed
if __name__ == '__main__':
    try:
        success = main()
        if success:
            print("\n✅ Test completed successfully")
        else:
            print("\n❌ Test completed with failures")
    except Exception as e:
        print(f"\n💥 Test crashed: {e}")
