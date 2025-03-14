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