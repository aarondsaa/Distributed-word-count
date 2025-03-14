# Distributed Word Count Lab

Welcome to the **Distributed Word Count Lab**! This repository demonstrates a simple approach to splitting a text-processing task across multiple Python “workers” using socket communication.

---

## Table of Contents
1. [Overview](#overview)  
2. [Prerequisites](#prerequisites)  
3. [Files in This Repository](#files-in-this-repository)  
4. [Step-by-Step Instructions](#step-by-step-instructions)  
5. [Troubleshooting](#troubleshooting)  
6. [Extensions](#extensions)

---

## Overview

In this mini-MapReduce style lab, you will:
- **Divide** a text into chunks.
- **Distribute** each chunk to a separate worker process (or machine).
- **Count** the words in each chunk.
- **Aggregate** the results back in the coordinator (master) process.

By completing this lab, you’ll gain hands-on experience with:
- Basic **socket** programming in Python.
- Managing **multiple processes** for parallel or distributed work.
- **Combining** partial results into a final output.

---

## Prerequisites

1. **Python 3.x** installed (check with `python --version` or `python3 --version`).
2. **Command-line** access to run multiple terminals (or a way to open multiple shell windows).
3. Basic knowledge of Python data structures (like dictionaries or `collections.Counter`).
4. Familiarity with **Git/GitHub** (to clone or download this repository).

---

## Files in This Repository

1. **`README.md`** (this file): Contains instructions and an overview of the lab.
2. **`worker.py`**: The worker script that listens for text chunks, counts words, and returns the result.
3. **`coordinator.py`**: The main coordinator script that splits the text and collects results.
4. (Optional) **`sample_input.txt`**: A sample text file you can use for testing.

---

## Step-by-Step Instructions

### 1. Clone or Download the Repository
```bash
git clone https://github.com/<your-username>/distributed-wordcount-lab.git
cd distributed-wordcount-lab
```
Or you can **download** the ZIP from GitHub and extract it locally.

### 2. Start the Worker Processes
You need one terminal per worker. In each terminal, navigate to the repository folder and run:
```bash
python worker.py 127.0.0.1 5001
```
For a second worker (in a **separate** terminal):
```bash
python worker.py 127.0.0.1 5002
```
- Adjust the ports (5001, 5002) if they are in use or if you want more workers.

### 3. Run the Coordinator
Open another terminal (third one) and run:
```bash
python coordinator.py
```
- The coordinator will split the text into chunks (for now, just two chunks for two workers), send them to each worker, and then receive/aggregate the word counts.

### 4. Observe the Output
- The coordinator will print out the **final word counts** in the terminal.
- Each worker will show logs indicating it received text and eventually a “DONE” signal.

---

## Worker Code

Below is the content of **`worker.py`** (for reference). It listens on a host/port, waits for a text chunk, counts words, and sends results back.

```python
import socket
import pickle
import collections

def main(worker_host, worker_port):
    # Create a server socket
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind((worker_host, worker_port))
    server_socket.listen(1)
    print(f"[Worker] Listening on {worker_host}:{worker_port}")

    while True:
        conn, addr = server_socket.accept()
        try:
            data = conn.recv(4096)
            if not data:
                break

            text_chunk = pickle.loads(data)
            if text_chunk == "DONE":
                print("[Worker] Received DONE signal. Shutting down.")
                conn.close()
                break

            # Count the words
            words = text_chunk.split()
            counts = collections.Counter(words)

            # Convert to dict and send back
            conn.sendall(pickle.dumps(dict(counts)))
        finally:
            conn.close()

if __name__ == "__main__":
    import sys
    """
    Usage: python worker.py <worker_host> <worker_port>
    Example: python worker.py 127.0.0.1 5001
    """
    worker_host = sys.argv[1]
    worker_port = int(sys.argv[2])
    main(worker_host, worker_port)
```

---

## Coordinator Code

Below is **`coordinator.py`**, which coordinates the entire process: splitting text, sending chunks to workers, and merging final counts.

```python
import socket
import pickle
import collections

def send_chunk_and_get_counts(worker_host, worker_port, text_chunk):
    """
    Connect to a worker, send the text chunk, and retrieve the word-count dictionary.
    """
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.connect((worker_host, worker_port))
    s.sendall(pickle.dumps(text_chunk))  # Send text chunk
    data = s.recv(4096)                  # Receive partial counts
    s.close()
    return pickle.loads(data)            # Return dictionary

def main():
    # Define workers (host, port). You can add more if needed.
    workers = [
        ("127.0.0.1", 5001),
        ("127.0.0.1", 5002),
    ]

    # A sample text for demonstration (you can replace or read from file)
    text = """
    hello world
    this is a simple test
    hello again
    distributed computing is fun
    """

    # Split text into lines
    lines = text.strip().split('\n')

    # Simple splitting into two chunks (for 2 workers)
    midpoint = len(lines) // 2
    chunk1 = "\n".join(lines[:midpoint])
    chunk2 = "\n".join(lines[midpoint:])

    chunks = [chunk1, chunk2]

    # Aggregate results here
    combined_counts = collections.Counter()

    # Distribute each chunk to corresponding worker
    for i, (host, port) in enumerate(workers):
        result_dict = send_chunk_and_get_counts(host, port, chunks[i])
        combined_counts.update(result_dict)

    # Print final word counts
    print("[Coordinator] Final Word Counts:")
    for word, count in combined_counts.items():
        print(f"{word}: {count}")

    # Send "DONE" to each worker so they shut down
    for (host, port) in workers:
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.connect((host, port))
        s.sendall(pickle.dumps("DONE"))
        s.close()

if __name__ == "__main__":
    main()
```

---

## Troubleshooting

1. **Port Already in Use**  
   - If you see an error like `OSError: [Errno 98] Address already in use`, pick a different port (e.g., 5003, 5004).

2. **Connection Refused**  
   - Make sure **workers are running first** before starting the coordinator.
   - Double-check you’re using the correct IP and port.

3. **Firewall Issues**  
   - Some systems block Python socket connections by default. Temporarily disable or allow these connections.

4. **Hanging or Crashing**  
   - Press `CTRL + C` to stop the coordinator or worker if things get stuck.
   - Double-check the code for typos or mismatch in host/port definitions.

---

## Extensions

1. **Multiple Workers**  
   - Add more `(host, port)` entries in the `workers` list in `coordinator.py`.  
   - Split your text accordingly into more chunks.

2. **Use a Real File**  
   - Replace the sample text in `coordinator.py` with something read from `sample_input.txt`.

3. **Failure Handling**  
   - What if a worker goes offline mid-task? Try handling the exception in the coordinator and re-sending.

4. **Load Balancing**  
   - If you have large text files, try distributing lines more evenly among workers.

---

### That’s It!
You now have a **working** mini-distributed system for word counting. Feel free to **experiment** further and push your updates back to this repo.
