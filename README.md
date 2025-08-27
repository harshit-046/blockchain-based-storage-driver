# 🔗 Blockchain-Backed FUSE Storage Driver

A user-space FUSE filesystem that stores file blocks on **IPFS** and secures them with a **blockchain-backed integrity mechanism**.

---

## ✅ Prerequisites

Before starting, make sure you have:

- Python **3.10+**
- **FUSE** (`libfuse-dev`)
- **IPFS 0.7.0**
- A working **virtual environment**

---

## 📦 Installation & Setup

1. **Clone the repository** (if not already):

   ```bash
   git clone https://github.com/yourusername/blockchain-fuse-storage.git
   cd blockchain-fuse-storage
   ```

2. **Create a virtual environment**:

   ```bash
   python3 -m venv .venv
   source .venv/bin/activate
   ```

3. **Install dependencies**:

   ```bash
   pip install -r requirements.txt
   ```

---

## 🔁 Restart & Usage Guide

### 1. **Activate your virtual environment**

```bash
source .venv/bin/activate
```

---

### 2. **Start IPFS daemon**

Open a **new terminal tab/window** and run:

```bash
ipfs daemon
```

Keep this terminal open and running.

---

### 3. **Ensure mountpoint directory exists**

```bash
mkdir -p ~/blockchain-mount
```

---

### 4. **Mount the FUSE filesystem**

In your main terminal (with `venv` activated):

```bash
python myfuse/main.py ~/blockchain-mount
```

You’ll see:

```
Mounting blockchain-backed filesystem at /home/harshit/blockchain-mount
Press Ctrl+C to unmount
```

Leave this terminal running until you're done testing.

---

## 🧪 Testing the Project

Open **another terminal** (leave the mount one running), then:

### ✅ 5. **Write and read files**

```bash
echo "Hello again!" > ~/blockchain-mount/test.txt
cat ~/blockchain-mount/test.txt
```

---

### ✅ 6. **Run the integrity checker**

Verify blockchain:

```bash
python myfuse/integrity_checker.py verify-blockchain
```

Verify a specific file:

```bash
python myfuse/integrity_checker.py verify-file --file test.txt
```

---

### ✅ 7. **Test large or multiple files (optional)**

Create a 1MB binary file:

```bash
dd if=/dev/zero of=~/blockchain-mount/large.bin bs=1024 count=1000
```

Create multiple test files:

```bash
for i in {1..5}; do echo "File $i" > ~/blockchain-mount/file_$i.txt; done
```

Benchmark:

```bash
time cat ~/blockchain-mount/large.bin > /dev/null
```

---

## 🧹 Shutting It Down Again (Clean Exit)

### 🔻 Unmount the filesystem:

Press `Ctrl+C` in the terminal running `main.py`.

Or manually:

```bash
fusermount -u ~/blockchain-mount
```

### 🔻 Stop IPFS daemon:

Press `Ctrl+C` in the IPFS terminal.

### 🔻 Deactivate virtual environment:

```bash
deactivate
```

---

## 📖 Notes

- You can change the mountpoint directory name (`~/blockchain-mount`) as needed.
- Make sure the **IPFS daemon** is always running in the background before mounting.
- Logs and blockchain data are stored in your project directory for debugging.
