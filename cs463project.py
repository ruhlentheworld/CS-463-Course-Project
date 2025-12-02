import time
import tracemalloc
import gc
from Crypto.Cipher import AES
import ascon
from simon import SimonCipher
from speck import SpeckCipher
import matplotlib.pyplot as plt

message_sizes = [64, 256, 1024, 4096]
runs = 6

key_aes = b"thequickbrownfox"
key_ascon = b"thequickbrownfox"
key_simon = int.from_bytes(b"thequickbrownfox"[:8], "big")
key_speck = int.from_bytes(b"thequickbrownfox"[:8], "big")
nonce = b"andthreelazydogs"
block_size_bytes = 8

def measure_peak(func):
    gc.collect()
    tracemalloc.start()
    start_time = time.perf_counter()
    func()
    end_time = time.perf_counter()
    current, peak = tracemalloc.get_traced_memory()
    tracemalloc.stop() 
    peak_mb = peak / 1_000_000
    runtime = end_time - start_time
    return runtime, peak_mb

def print_avg(cipher, size, avg_time, avg_mem):
    print(f"{cipher} {size} byte | Average Time: {avg_time:.6f} sec | Average Memory Used: {avg_mem:.6f} MB")

def print_total(cipher, tottime, peak_bytes):
    print(f"{cipher} Totals | Time: {tottime:.6f} sec | Peak Memory: {peak_bytes/1_000_000:.6f} MB")

def run_aes(size):
    times, mem = [], []

    for run in range(1, runs + 1):
        message = (b"jumpedoverazebra" * ((size // 16) + 1))[:size]

        def task():
            cipher = AES.new(key_aes, AES.MODE_ECB)
            ct = cipher.encrypt(message.ljust((len(message)//16 + 1)*16, b'\0'))
            pt = cipher.decrypt(ct).rstrip(b'\0')
            assert pt == message

        runtime, peak_mb = measure_peak(task)

        if run > 1:
            times.append(runtime)
            mem.append(peak_mb)
            print(f"Run {run-1}")
            print(f"  Time {runtime:.6f} sec | Mem {peak_mb:.6f} MB")

    return times, mem

def run_ascon(size):
    times, mem = [], []

    for run in range(1, runs + 1):
        message = (b"jumpedoverazebra" * ((size // 16) + 1))[:size]

        def task():
            ct = ascon.encrypt(key_ascon, nonce, b"", message, variant="Ascon-128")
            pt = ascon.decrypt(key_ascon, nonce, b"", ct, variant="Ascon-128")
            assert pt == message

        runtime, peak_mb = measure_peak(task)
        
        if run > 1:
            times.append(runtime)
            mem.append(peak_mb)
            print(f"Run {run-1}")
            print(f"  Time {runtime:.6f} sec | Mem {peak_mb:.6f} MB")

    return times, mem

def run_simon(size):
    times, mem = [], []

    for run in range(1, runs + 1):
        message = (b"jumpedoverazebra" * ((size // 16) + 1))[:size]

        def task():
            cipher = SimonCipher(key_simon)
            blocks = []
            for i in range(0, len(message), block_size_bytes):
                b = message[i:i+block_size_bytes].ljust(block_size_bytes, b"\0")
                blocks.append(cipher.encrypt(int.from_bytes(b, "big")))
            out = b""
            for c in blocks:
                out += cipher.decrypt(c).to_bytes(block_size_bytes, "big")
            out = out[:len(message)]
            assert out == message

        runtime, peak_mb = measure_peak(task)
        
        if run > 1:
            times.append(runtime)
            mem.append(peak_mb)
            print(f"Run {run-1}")
            print(f"  Time {runtime:.6f} sec | Mem {peak_mb:.6f} MB")

    return times, mem

def run_speck(size):
    times, mem = [], []

    for run in range(1, runs + 1):
        message = (b"jumpedoverazebra" * ((size // 16) + 1))[:size]

        def task():
            cipher = SpeckCipher(key_speck)
            blocks = []
            for i in range(0, len(message), block_size_bytes):
                b = message[i:i+block_size_bytes].ljust(block_size_bytes, b"\0")
                blocks.append(cipher.encrypt(int.from_bytes(b, "big")))
            out = b""
            for c in blocks:
                out += cipher.decrypt(c).to_bytes(block_size_bytes, "big")
            out = out[:len(message)]
            assert out == message

        runtime, peak_mb = measure_peak(task)
        
        if run > 1:
            times.append(runtime)
            mem.append(peak_mb)
            print(f"Run {run-1}")
            print(f"  Time {runtime:.6f} sec | Mem {peak_mb:.6f} MB")

    return times, mem

totals = {
    "AES-128": {"total_time": 0.0, "peak_mem_bytes": 0},
    "Ascon":   {"total_time": 0.0, "peak_mem_bytes": 0},
    "Simon":   {"total_time": 0.0, "peak_mem_bytes": 0},
    "Speck":   {"total_time": 0.0, "peak_mem_bytes": 0},
}

tracemalloc.start()

per_size_results = {size: {} for size in message_sizes}

for size in message_sizes:
    print(f"\n{size} Byte Tests")
    
    for cipher_name in ["AES-128", "Ascon", "Simon", "Speck"]:
        print(f"\n{cipher_name}: {size} bytes")

        if cipher_name == "AES-128":
            times, mem = run_aes(size)

        elif cipher_name == "Ascon":
            times, mem = run_ascon(size)

        elif cipher_name == "Simon":
            times, mem = run_simon(size)

        elif cipher_name == "Speck":
            times, mem = run_speck(size)

        totals[cipher_name]["total_time"] += sum(times)
        totals[cipher_name]["peak_mem_bytes"] = max(
            totals[cipher_name]["peak_mem_bytes"],
            max(mem) * 1_000_000
        )

        avg_time = sum(times) / (runs-1)
        avg_mem = sum(mem) / (runs-1)

        print("-" * 82)
        print_avg(cipher_name, size, avg_time, avg_mem)

        per_size_results[size][cipher_name] = {
            "avg_time": avg_time,
            "avg_mem": avg_mem,
        }

    print("\n" + "-" * 82)
    print(f"{size} byte Winners sorted by Efficiency Ratio")
    print("-" * 82)
 
    winners = []
    for cipher_name in ["AES-128", "Ascon", "Simon", "Speck"]:
        pdata = per_size_results[size][cipher_name]
        peak_mem_size = pdata["avg_mem"]
        total_time_size = pdata["avg_time"]  
        ratio = (peak_mem_size / total_time_size) if total_time_size > 0 else float("inf")
        winners.append((
            cipher_name,
            ratio,
            pdata["avg_time"],
            pdata["avg_mem"],
        ))

    winners_sorted = sorted(winners, key=lambda x: x[1])

    print(f"{'Rank':<6} {'Cipher':<10} {'Time Used':>14} {'Memory Used':>13} {'Efficiency Ratio':>21}")
    print("-" * 82)

    for rank, item in enumerate(winners_sorted, start=1):
        name, ratio, avg_time, avg_mem = item
        print(f"{rank:<6} {name:<10} {avg_time:10.6f} sec {avg_mem:10.6f} MB {ratio:14.6f} MB/sec")

print("\n" + "*" * 82)
print("Cipher Totals & Efficiency Ratios (across all sizes, combined runs)")
print("*" * 82)

final_results = []
for name, data in totals.items():
    total_time = float(data["total_time"])
    peak_bytes = int(data["peak_mem_bytes"])
    peak_mb = peak_bytes / 1_000_000
    ratio = peak_mb / total_time if total_time > 0 else float("inf")
    final_results.append((name, total_time, peak_mb, ratio))

print(f"{'Cipher':<10} {'Time Used':>16} {'Memory Used':>18} {'Efficiency Ratio':>25}")
print("-" * 72)
for name, total_time, peak_mb, ratio in final_results:
    print(f"{name:<10} {total_time:12.6f} sec {peak_mb:15.6f} MB {ratio:18.6f} MB/sec")

print("\n" + "=" * 82)
print("Efficiency Rankings")
print("=" * 82)

ranked = sorted(final_results, key=lambda x: x[3])

print(f"\n{'Rank':<6} {'Cipher':<10} {'Efficiency Ratio':>27}")
print("-" * 45)
for i, (name, _, _, ratio) in enumerate(ranked, 1):
    print(f"{i:<6} {name:<10} {ratio:20.6f} MB/sec")

tracemalloc.stop()

ciphers = ["AES-128", "Ascon", "Simon", "Speck"]

times_plot = {cipher: [] for cipher in ciphers}
mem_plot   = {cipher: [] for cipher in ciphers}
ratio_plot = {cipher: [] for cipher in ciphers}

for size in message_sizes:
    for cipher in ciphers:
        t = per_size_results[size][cipher]["avg_time"]
        m = per_size_results[size][cipher]["avg_mem"]
        r = m / t if t > 0 else float("inf")
        times_plot[cipher].append(t)
        mem_plot[cipher].append(m)
        ratio_plot[cipher].append(r)

plt.figure(figsize=(10,6))
for cipher in ciphers:
    plt.plot(message_sizes, times_plot[cipher], marker='o', label=cipher)

plt.xlabel("Message Size (bytes)")
plt.ylabel("Average Runtime (seconds)")
plt.title("Cipher Runtime vs Message Size")
plt.grid(True)
plt.legend()
plt.xticks(message_sizes)
plt.tight_layout()
plt.show()

plt.figure(figsize=(10,6))
for cipher in ciphers:
    plt.plot(message_sizes, mem_plot[cipher], marker='o', label=cipher)

plt.xlabel("Message Size (bytes)")
plt.ylabel("Average Memory Used (MB)")
plt.title("Cipher Memory Usage vs Message Size")
plt.grid(True)
plt.legend()
plt.xticks(message_sizes)
plt.tight_layout()
plt.show()

plt.figure(figsize=(10,6))
for cipher in ciphers:
    plt.plot(message_sizes, ratio_plot[cipher], marker='o', label=cipher)

plt.xlabel("Message Size (bytes)")
plt.ylabel("Efficiency Ratio (MB / sec)")
plt.title("Cipher Efficiency Ratio vs Message Size")
plt.grid(True)
plt.legend()
plt.xticks(message_sizes)
plt.tight_layout()
plt.show()
