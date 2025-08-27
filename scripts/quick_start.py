"""
Quick start script to set up and test the blockchain FUSE filesystem.
"""

import os
import sys
import subprocess
import time
import signal

def check_dependencies():
    """Check if required dependencies are installed."""
    print("🔍 Checking dependencies...")
    
    # Check Python packages
    packages = ['fuse', 'ipfshttpclient']
    missing_packages = []
    
    for package in packages:
        try:
            __import__(package)
            print(f"   ✅ {package}")
        except ImportError:
            missing_packages.append(package)
            print(f"   ❌ {package}")
    
    if missing_packages:
        print(f"\n📦 Installing missing packages: {missing_packages}")
        for package in missing_packages:
            if package == 'fuse':
                package = 'fusepy'
            
            try:
                subprocess.check_call([sys.executable, '-m', 'pip', 'install', package])
                print(f"   ✅ Installed {package}")
            except subprocess.CalledProcessError:
                print(f"   ❌ Failed to install {package}")
                return False
    
    return True

def check_ipfs():
    """Check if IPFS is running."""
    print("\n🌐 Checking IPFS...")
    
    try:
        result = subprocess.run(['ipfs', 'id'], capture_output=True, text=True, timeout=5)
        if result.returncode == 0:
            print("   ✅ IPFS daemon is running")
            return True
        else:
            print("   ❌ IPFS daemon not responding")
            return False
    except (subprocess.TimeoutExpired, FileNotFoundError):
        print("   ❌ IPFS not found or not running")
        print("   💡 Start IPFS with: ipfs daemon")
        return False

def setup_directories():
    """Create necessary directories."""
    print("\n📁 Setting up directories...")
    
    directories = ['mountpoint', 'myfuse']
    
    for directory in directories:
        os.makedirs(directory, exist_ok=True)
        print(f"   ✅ {directory}/")

def start_filesystem():
    """Start the FUSE filesystem."""
    print("\n🚀 Starting blockchain FUSE filesystem...")
    
    try:
        # Start the filesystem in the background
        process = subprocess.Popen([
            sys.executable, 'myfuse/main.py', './mountpoint'
        ], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        
        # Give it time to mount
        time.sleep(3)
        
        # Check if it's still running
        if process.poll() is None:
            print("   ✅ Filesystem started successfully")
            print("   📂 Mounted at: ./mountpoint")
            return process
        else:
            stdout, stderr = process.communicate()
            print("   ❌ Filesystem failed to start")
            print(f"   Error: {stderr.decode()}")
            return None
            
    except Exception as e:
        print(f"   ❌ Failed to start filesystem: {e}")
        return None

def run_quick_test():
    """Run a quick functionality test."""
    print("\n🧪 Running quick test...")
    
    try:
        # Test file creation
        test_file = './mountpoint/quick_test.txt'
        test_content = "Quick test of blockchain filesystem!"
        
        with open(test_file, 'w') as f:
            f.write(test_content)
        print("   ✅ File write successful")
        
        # Test file reading
        with open(test_file, 'r') as f:
            read_content = f.read()
        
        if read_content == test_content:
            print("   ✅ File read successful")
        else:
            print("   ❌ File content mismatch")
            return False
        
        # Test directory listing
        files = os.listdir('./mountpoint')
        if 'quick_test.txt' in files:
            print("   ✅ Directory listing successful")
        else:
            print("   ❌ File not found in directory listing")
            return False
        
        print("   🎉 Quick test passed!")
        return True
        
    except Exception as e:
        print(f"   ❌ Quick test failed: {e}")
        return False

def show_usage_examples():
    """Show usage examples."""
    print("\n💡 Usage Examples:")
    print("   # Create a file")
    print("   echo 'Hello blockchain!' > ./mountpoint/hello.txt")
    print()
    print("   # Read a file")
    print("   cat ./mountpoint/hello.txt")
    print()
    print("   # List files")
    print("   ls -la ./mountpoint/")
    print()
    print("   # Verify blockchain")
    print("   python myfuse/integrity_checker.py verify-blockchain")
    print()
    print("   # Verify specific file")
    print("   python myfuse/integrity_checker.py verify-file --file hello.txt")
    print()
    print("   # Show blockchain info")
    print("   python myfuse/integrity_checker.py info")

def main():
    """Main quick start function."""
    print("🚀 Blockchain FUSE Filesystem Quick Start")
    print("=" * 50)
    
    # Check dependencies
    if not check_dependencies():
        print("\n❌ Dependency check failed. Please install missing packages.")
        return False
    
    # Check IPFS
    if not check_ipfs():
        print("\n❌ IPFS check failed. Please start IPFS daemon first.")
        print("   Run: ipfs daemon")
        return False
    
    # Setup directories
    setup_directories()
    
    print("\n📋 Setup completed successfully!")
    print("\n🎯 Next steps:")
    print("   1. Start IPFS daemon: ipfs daemon")
    print("   2. Start filesystem: python myfuse/main.py ./mountpoint")
    print("   3. Test filesystem: python scripts/simple_test.py")
    
    return True

# Run setup when executed
if __name__ == '__main__':
    try:
        success = main()
        if success:
            print("\n✅ Quick start completed successfully")
        else:
            print("\n❌ Quick start failed")
    except Exception as e:
        print(f"\n💥 Quick start crashed: {e}")
