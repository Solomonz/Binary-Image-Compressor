from sys import argv
from math import ceil, inf, log2
import json
import os


def num_to_bits(n, num_bits):
    assert(0 <= n < 2**num_bits)
    return [1 if n & 2**i else 0 for i in range(num_bits - 1, -1, -1)]


def calculate_pairwise_encoding(bit_array, zero_len, one_len):
    max_zeros = 2**zero_len - 1
    max_ones = 2**one_len - 1

    out = []
    cur_run_bit = 0
    cur_run_len = 0
    i = 0

    while i < len(bit_array):
        cur_max_len = (max_ones if cur_run_bit else max_zeros)
        if bit_array[i] == cur_run_bit and cur_run_len < cur_max_len:
            cur_run_len += 1
            i += 1
        else:
            out.extend(num_to_bits(cur_run_len, one_len if cur_run_bit else zero_len))
            cur_run_len = 0
            cur_run_bit = 1 - cur_run_bit
    out.extend(num_to_bits(cur_run_len, one_len if cur_run_bit else zero_len))
    return ceil((len(out) + 4 + 4) / 8), out


def calculate_pairwise_encoding_with_LEB(bit_array, zero_len, one_len):
    max_zeros = 2**zero_len - 1
    max_ones = 2**one_len - 1

    out = []
    total_num_bits = 0
    cur_run_bit = 0
    cur_run_len = 0
    i = 0

    while i < len(bit_array):
        cur_max_len = (max_ones if cur_run_bit else max_zeros)
        if bit_array[i] == cur_run_bit and cur_run_len < cur_max_len:
            cur_run_len += 1
            i += 1
        else:
            pass
            # out.extend()


def calculate_bit_prefix_encoding(bit_array, num_len_bits):
    max_len = 2**num_len_bits - 1

    out = []
    cur_run_bit = bit_array[0]
    cur_run_len = 0
    i = 0

    while i < len(bit_array):
        if bit_array[i] == cur_run_bit and cur_run_len < max_len:
            cur_run_len += 1
            i += 1
        else:
            out.extend([cur_run_bit] + num_to_bits(cur_run_len, num_len_bits))
            cur_run_len = 0
            cur_run_bit = bit_array[i]
    out.extend([cur_run_bit] + num_to_bits(cur_run_len, num_len_bits))
    return ceil((len(out) + 4) / 8), out
    

def encode_optimal_pairwise(bit_array):
    best_byte_size = inf
    best_pairwise_num_bits = (None, None)
    best_pairwise_encoded = None
    pairwise_sizes = []
    for i in range(1, 13):
        i_sizes = []
        for j in range(1, 13):
            num_bytes, encoded = calculate_pairwise_encoding(bit_array, i, j)
            if num_bytes < best_byte_size:
                best_byte_size = num_bytes
                best_pairwise_num_bits = (i, j)
                best_pairwise_encoded = encoded
    return best_byte_size, best_pairwise_encoded


def encode_optimal_bit_prefix(bit_array):
    best_byte_size = 512
    best_bit_size = None
    best_encoded = None
    for i in range(1, 13):
        num_bytes, encoded = calculate_bit_prefix_encoding(bit_array, i)
        if num_bytes < best_byte_size:
            best_byte_size = num_bytes
            best_bit_size = i
            best_encoded = encoded
    return best_byte_size, best_encoded


def encode_optimal_naive(bit_array):
    num_bytes = ceil(len(bit_array) / 8)
    return num_bytes, bit_array


def encode_optimal_monospace(bit_array):
    max_run_len = 0
    cur_run_len = 1
    num_runs = 1
    for i in range(1, len(bit_array)):
        if bit_array[i] == bit_array[i - 1]:
            cur_run_len += 1
        else:
            cur_run_len = 1
            num_runs += 1
        max_run_len = max(max_run_len, cur_run_len)
    bits_per_run = ceil(log2(max_run_len + 1))
    total_bits = bits_per_run * num_runs
    num_bytes = ceil(total_bits / 8)
    serialized_out = [] # unimplemented
    return num_bytes, serialized_out


ENCODERS = [
    encode_optimal_bit_prefix,
    encode_optimal_pairwise,
    encode_optimal_naive,
    encode_optimal_monospace,
]


def test_whole_suite():
    script_dir = os.path.dirname(__file__)
    json_fpath = os.path.join(script_dir, "images/keyboard_images.json")
    json_pixels = json.load(open(json_fpath))

    algos = [(algo.__name__, algo) for algo in ENCODERS]
    # algo name => (sum, min, max)
    summary_data = { algo_name: (0, inf, 0) for (algo_name, _) in algos}
    for img_name in json_pixels:
        print(f"Case {img_name}")
        pixel_str = json_pixels[img_name]
        img_pixels = [int(c) for c in pixel_str]
        min_bytes_per_img = 0
        for idx, (algo_name, algo) in enumerate(algos):
            num_bytes, _ = algo(img_pixels)
            best_byte_size = min(min_bytes_per_img, num_bytes)
            cur_sum, cur_min, cur_max = summary_data[algo_name]
            cur_sum += num_bytes
            cur_min = min(cur_min, num_bytes)
            cur_max = max(cur_max, num_bytes)
            summary_data[algo_name] = cur_sum, cur_min, cur_max 
            print(f"  {algo_name} used {num_bytes} bytes")

    print("\n**SUMMARY**")
    for algo_name in summary_data:
        print(f"{algo_name}:")
        cur_sum, cur_min, cur_max = summary_data[algo_name]
        avg = ceil(cur_sum / len(json_pixels))
        print(f"  total bytes used: {cur_sum} avg: {avg} min: {cur_min} max: {cur_max}")


if __name__ == "__main__":
    test_whole_suite()
