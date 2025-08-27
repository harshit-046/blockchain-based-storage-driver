"""
Basic test script for the blockchain FUSE filesystem.
Works in any Python environment without complex argument parsing.
"""

import os
import sys
import json
import subprocess

def test_environment():
    """Test the basic environment setup."""
    print("🔍 Testing Environment Setup")
    print("-" * 30)
    
    # Check if required files exist
    required_files = [
        'myfuse/main.py',
        'myfuse/blockchain.py',
        'myfuse/ipfs_client.py',
        'myfuse/integrity_checker.py',
        'myfuse/config.py',
        'myfuse/log.py'
    ]
    
    missing_files = []
    for file_path in required_files:
        if os.path.exists(file_path):
            print(f"   ✅ {file_path}")
        else:
            print(f"   ❌ {file_path}")
            missing_files.append(file_path)
    
    if missing_files:
        print(f"\n❌ Missing files: {missing_files}")
        print("\n💡 SOLUTION: The project files need to be created first!")
        print("   Run the setup script to create all necessary files:")
        print("   python scripts/create_project_files.py")
        return False
    
    print("✅ All required files present")
    return True

def test_python_imports():
    """Test if required Python packages can be imported."""
    print("\n🐍 Testing Python Imports")
    print("-" * 30)
    
    packages = [
        ('json', 'json'),
        ('hashlib', 'hashlib'),
        ('datetime', 'datetime'),
        ('os', 'os'),
        ('sys', 'sys')
    ]
    
    # Test optional packages
    optional_packages = [
        ('fuse', 'fusepy'),
        ('ipfshttpclient', 'ipfshttpclient')
    ]
    
    all_good = True
    
    # Test required packages
    for module_name, package_name in packages:
        try:
            __import__(module_name)
            print(f"   ✅ {package_name}")
        except ImportError:
            print(f"   ❌ {package_name}")
            all_good = False
    
    # Test optional packages
    for module_name, package_name in optional_packages:
        try:
            __import__(module_name)
            print(f"   ✅ {package_name}")
        except ImportError:
            print(f"   ⚠️  {package_name} (install with: pip install {package_name})")
    
    return all_good

def test_ipfs_availability():
    """Test if IPFS is available."""
    print("\n🌐 Testing IPFS Availability")
    print("-" * 30)
    
    try:
        result = subprocess.run(['ipfs', 'version'], 
                              capture_output=True, text=True, timeout=5)
        if result.returncode == 0:
            version_info = result.stdout.strip()
            print(f"   ✅ IPFS found: {version_info}")
            
            # Test if daemon is running
            try:
                daemon_result = subprocess.run(['ipfs', 'id'], 
                                             capture_output=True, text=True, timeout=5)
                if daemon_result.returncode == 0:
                    print("   ✅ IPFS daemon is running")
                    return True
                else:
                    print("   ⚠️  IPFS daemon not running (start with: ipfs daemon)")
                    return False
            except:
                print("   ⚠️  IPFS daemon status unknown")
                return False
        else:
            print("   ❌ IPFS not responding")
            return False
    except (subprocess.TimeoutExpired, FileNotFoundError):
        print("   ❌ IPFS not found")
        print("   💡 Install IPFS from: https://ipfs.io/")
        return False

def test_blockchain_creation():
    """Test blockchain creation and basic operations."""
    print("\n🔗 Testing Blockchain Creation")
    print("-" * 30)
    
    try:
        # Import blockchain module
        sys.path.append('myfuse')
        from blockchain import Blockchain
        
        # Create a test blockchain
        test_blockchain = Blockchain('test_blockchain.json')
        
        print("   ✅ Blockchain class imported")
        print(f"   ✅ Blockchain created with {len(test_blockchain.chain)} blocks")
        
        # Test blockchain validation
        is_valid = test_blockchain.validate_chain()
        if is_valid:
            print("   ✅ Blockchain validation passed")
        else:
            print("   ❌ Blockchain validation failed")
        
        # Clean up test file
        if os.path.exists('test_blockchain.json'):
            os.remove('test_blockchain.json')
        
        return is_valid
        
    except Exception as e:
        print(f"   ❌ Blockchain test failed: {e}")
        return False

def test_directory_structure():
    """Test and create necessary directory structure."""
    print("\n📁 Testing Directory Structure")
    print("-" * 30)
    
    directories = ['mountpoint', 'myfuse']
    
    for directory in directories:
        if os.path.exists(directory):
            print(f"   ✅ {directory}/ exists")
        else:
            try:
                os.makedirs(directory, exist_ok=True)
                print(f"   ✅ {directory}/ created")
            except Exception as e:
                print(f"   ❌ Failed to create {directory}/: {e}")
                return False
    
    return True

def test_config_loading():
    """Test configuration loading."""
    print("\n⚙️  Testing Configuration")
    print("-" * 30)
    
    try:
        sys.path.append('myfuse')
        import config
        
        print(f"   ✅ IPFS Host: {config.IPFS_HOST}")
        print(f"   ✅ IPFS Port: {config.IPFS_PORT}")
        print(f"   ✅ Chunk Size: {config.CHUNK_SIZE}")
        print(f"   ✅ Difficulty: {config.DIFFICULTY}")
        print(f"   ✅ Blockchain File: {config.BLOCKCHAIN_FILE}")
        
        return True
        
    except Exception as e:
        print(f"   ❌ Config loading failed: {e}")
        return False

def show_next_steps():
    """Show next steps for the user."""
    print("\n🎯 Next Steps")
    print("-" * 30)
    print("1. Start IPFS daemon:")
    print("   ipfs daemon")
    print()
    print("2. Start the filesystem (in another terminal):")
    print("   python myfuse/main.py ./mountpoint")
    print()
    print("3. Test file operations (in another terminal):")
    print("   echo 'Hello blockchain!' > ./mountpoint/test.txt")
    print("   cat ./mountpoint/test.txt")
    print()
    print("4. Verify blockchain integrity:")
    print("   python myfuse/integrity_checker.py verify-blockchain")
    print()
    print("5. Verify specific file:")
    print("   python myfuse/integrity_checker.py verify-file --file test.txt")

def run_all_tests():
    """Run all basic tests."""
    print("🧪 Blockchain FUSE Filesystem - Basic Tests")
    print("=" * 50)
    
    tests = [
        ("Environment Setup", test_environment),
        ("Python Imports", test_python_imports),
        ("IPFS Availability", test_ipfs_availability),
        ("Directory Structure", test_directory_structure),
        ("Configuration", test_config_loading),
        ("Blockchain Creation", test_blockchain_creation),
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        try:
            if test_func():
                passed += 1
            else:
                print(f"   ⚠️ {test_name} had issues")
        except Exception as e:
            print(f"   💥 {test_name} crashed: {e}")
    
    print("\n" + "=" * 50)
    print(f"📊 Test Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All basic tests passed!")
        show_next_steps()
    elif passed >= total - 1:
        print("✅ Most tests passed - system should work")
        show_next_steps()
    else:
        print("⚠️ Several tests failed - check setup")
        print("\n🔧 Common Issues:")
        print("   • Install missing packages: pip install fusepy ipfshttpclient")
        print("   • Install IPFS: https://ipfs.io/")
        print("   • Start IPFS daemon: ipfs daemon")
    
    return passed >= total - 1

# Run tests when executed
if __name__ == '__main__':
    try:
        success = run_all_tests()
        print(f"\n{'✅ Success' if success else '❌ Failed'}")
    except KeyboardInterrupt:
        print("\n❌ Tests interrupted by user")
    except Exception as e:
        print(f"\n💥 Tests crashed: {e}")

# Also run when imported (for execution environment)
try:
    success = run_all_tests()
    print(f"\n{'✅ Basic tests completed successfully' if success else '❌ Basic tests completed with issues'}")
except Exception as e:
    print(f"\n💥 Basic tests crashed: {e}")
