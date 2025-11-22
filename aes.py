from Crypto.Cipher import AES
from Crypto.Random import get_random_bytes
import time
from memory_profiler import memory_usage

def encrypt(data, key):
    cipher = AES.new(key, AES.MODE_EAX)
    ciphertext, tag = cipher.encrypt_and_digest(data)
    return cipher.nonce, ciphertext, tag

def decrypt(nonce, ciphertext, tag, key):
    cipher = AES.new(key, AES.MODE_EAX, nonce=nonce)
    return cipher.decrypt_and_verify(ciphertext, tag)

def benchmark(message_size):
    key = get_random_bytes(16)  # AES-128 key (16 bytes)
    data = b"A" * message_size  # test message
    
    start_time = time.time()
    mem_before = memory_usage()[0]
    
    nonce, ciphertext, tag = encrypt(data, key)
    
    mem_after = memory_usage()[0]
    end_time = time.time()

    return (end_time - start_time), (mem_after - mem_before)

if __name__ == "__main__":
    sizes = [64, 256, 1024, 4096]  # 64B, 256B, 1KB, 4KB
    print("AES-128 Benchmark Results (Time in seconds, Memory in MB):\n")
    
    for size in sizes:
        runtime, mem_used = benchmark(size)
        print(f"Message Size: {size} bytes | Time: {runtime:.6f} sec | Memory Change: {mem_used:.6f} MB")
