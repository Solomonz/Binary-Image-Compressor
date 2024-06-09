from sys import argv
from math import ceil, inf
import json
import os


def num_to_bits(n, num_bits):
    assert(0 <= n < 2**num_bits)
    return [1 if n & 2**i else 0 for i in range(num_bits - 1, -1, -1)]


def bit_array_to_run_length_array(bit_array):
    out = []
    cur_bit = bit_array[0]
    cur_run_len = 0
    for b in bit_array:
        if b == cur_bit:
            cur_run_len += 1
        else:
            out.append(cur_run_len)
            cur_run_len = 1
            cur_bit = b
    out.append(cur_run_len)
    return out, bit_array[0]


def calculate_pairwise_encoding(run_length_array, first_bit, zero_len, one_len):
    max_zeros = 2**zero_len - 1
    max_ones = 2**one_len - 1

    out = []
    cur_run_bit = first_bit

    for r in run_length_array:
        cur_max_len = max_ones if cur_run_bit else max_zeros
        cur_bit_len = one_len if cur_run_bit else zero_len
        alternate_bit_len = zero_len if cur_run_bit else one_len
        while r > cur_max_len:
            out.extend(num_to_bits(cur_max_len, cur_bit_len))
            out.extend(num_to_bits(0, alternate_bit_len))
            r -= cur_max_len
        out.extend(num_to_bits(r, cur_bit_len))
        cur_run_bit = 1 - cur_run_bit
    return ceil((len(out) + 4 + 4 + 1) / 8), out


def calculate_pairwise_encoding_with_LEB(bit_array, zero_len, one_len):
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
            pass
            # out.extend()


def calculate_bit_prefix_encoding(run_length_array, first_bit, num_len_bits):
    max_len = 2**num_len_bits - 1

    out = []
    cur_run_bit = run_length_array[0]

    for r in run_length_array:
        while r > max_len:
            out.extend([cur_run_bit] + num_to_bits(max_len, num_len_bits))
            r -= max_len
        out.extend([cur_run_bit] + num_to_bits(r, num_len_bits))
        cur_run_bit = 1 - cur_run_bit
    return ceil((len(out) + 4) / 8), out
    

def encode_optimal_pairwise(bit_array):
    best_byte_size = inf
    best_num_bits = (None, None)
    best_encoded = None
    run_length_array, first_bit = bit_array_to_run_length_array(bit_array)
    for i in range(1, 13):
        for j in range(1, 13):
            num_bytes, encoded = calculate_pairwise_encoding(run_length_array, first_bit, i, j)
            if num_bytes < best_byte_size:
                best_byte_size = num_bytes
                best_num_bits = (i, j)
                best_encoded = encoded
    return best_byte_size, best_encoded


def encode_optimal_bit_prefix(bit_array):
    best_byte_size = inf
    best_num_bits = None
    best_encoded = None
    run_length_array, first_bit = bit_array_to_run_length_array(bit_array)
    for i in range(1, 13):
        num_bytes, encoded = calculate_bit_prefix_encoding(run_length_array, first_bit, i)
        if num_bytes < best_byte_size:
            best_byte_size = num_bytes
            best_num_bits = i
            best_encoded = encoded
    return best_byte_size, best_encoded


def encode_optimal_naive(bit_array):
    num_bytes = ceil(len(bit_array) / 8)
    return num_bytes, bit_array


ENCODERS = [encode_optimal_bit_prefix, encode_optimal_pairwise, encode_optimal_naive]


def test_whole_suite():
    script_dir = os.path.dirname(__file__)
    json_fpath = os.path.join(script_dir, "images/keyboard_images.json")
    json_pixels = json.load(open(json_fpath))

    algos = [(algo.__name__, algo) for algo in ENCODERS]
    # algo name => (sum, mean, min, max)
    summary_data = { algo_name: (0, inf, 0) for (algo_name, _) in algos}
    for img_name in json_pixels:
        print(f"Case {img_name}")
        pixel_str = json_pixels[img_name]
        img_pixels = [int(c) for c in pixel_str]
        for idx, (algo_name, algo) in enumerate(algos):
            num_bytes, _ = algo(img_pixels)
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
    print(calculate_pairwise_encoding([4, 6, 1], 0, 2, 2))
    print(calculate_bit_prefix_encoding([4, 1], 0, 2))
    test_whole_suite()
