from sys import argv
from math import ceil, inf, log2
import json
import os


def num_to_bits(n, num_bits):
    assert 0 <= n < 2**num_bits
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


def calculate_pairwise_encoding_with_LEB(
    run_length_array, first_bit, zero_len, one_len
):
    max_zeros = 2**zero_len - 1
    max_ones = 2**one_len - 1

    out = []
    cur_run_bit = 0

    for r in run_length_array:
        cur_max_len = max_ones if cur_run_bit else max_zeros
        cur_bit_len = one_len if cur_run_bit else zero_len
        alternate_bit_len = zero_len if cur_run_bit else one_len
        required_bits = ceil(log2(r + 1))
        required_units = ceil(required_bits / cur_bit_len)
        bits = num_to_bits(r, required_units * cur_bit_len)
        for u in range(required_units - 1):
            out.extend(bits[u * cur_bit_len : (u + 1) * cur_bit_len])
            out.extend(num_to_bits(0, alternate_bit_len))
        out.extend(bits[(required_units - 1) * cur_bit_len :])
        cur_run_bit = 1 - cur_run_bit
    return ceil((len(out) + 4 + 4 + 1) / 8), out


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
            num_bytes, encoded = calculate_pairwise_encoding(
                run_length_array, first_bit, i, j
            )
            if num_bytes < best_byte_size:
                best_byte_size = num_bytes
                best_num_bits = (i, j)
                best_encoded = encoded
    return best_byte_size, best_encoded


def encode_optimal_pairwise_LEB(bit_array):
    best_byte_size = inf
    best_num_bits = (None, None)
    best_encoded = None
    run_length_array, first_bit = bit_array_to_run_length_array(bit_array)
    for i in range(1, 13):
        for j in range(1, 13):
            num_bytes, encoded = calculate_pairwise_encoding_with_LEB(
                run_length_array, first_bit, i, j
            )
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
        num_bytes, encoded = calculate_bit_prefix_encoding(
            run_length_array, first_bit, i
        )
        if num_bytes < best_byte_size:
            best_byte_size = num_bytes
            best_num_bits = i
            best_encoded = encoded
    return best_byte_size, best_encoded


def encode_optimal_naive(bit_array):
    num_bytes = ceil(len(bit_array) / 8)
    return num_bytes, bit_array


def encode_optimal_monospace(bit_array):
    run_length_array, first_bit = bit_array_to_run_length_array(bit_array)
    max_run_len = max(run_length_array)
    bits_per_run = ceil(log2(max_run_len + 1))
    begin_bit_cost = 1
    bitsize_metadata_cost = 4
    total_bits = (
        bits_per_run * len(run_length_array) + begin_bit_cost + bitsize_metadata_cost
    )
    num_bytes = ceil(total_bits / 8)
    serialized_out = []  # unimplemented
    return num_bytes, serialized_out


ENCODERS = [
    encode_optimal_naive,
    encode_optimal_monospace,
    encode_optimal_bit_prefix,
    encode_optimal_pairwise,
    encode_optimal_pairwise_LEB,
]


def test_whole_suite():
    script_dir = os.path.dirname(__file__)
    json_fpath = os.path.join(script_dir, "images/keyboard_images.json")
    json_pixels = json.load(open(json_fpath))
    num_images = len(json_pixels)

    algos = [(algo.__name__, algo) for algo in ENCODERS]
    summary_data = {
        algo_name: {"wins": 0, "sum": 0, "min": inf, "max": 0}
        for (algo_name, _) in algos
    }
    for img_name in json_pixels:
        print(f"Case {img_name}")
        pixel_str = json_pixels[img_name]
        img_pixels = [int(c) for c in pixel_str]
        min_bytes_this_img = inf
        algo_to_byte_size = {}
        for idx, (algo_name, algo) in enumerate(algos):
            num_bytes, _ = algo(img_pixels)
            if num_bytes < min_bytes_this_img:
                min_bytes_this_img = num_bytes
            algo_stats = summary_data[algo_name]
            algo_stats["sum"] += num_bytes
            algo_stats["min"] = min(algo_stats["min"], num_bytes)
            algo_stats["max"] = max(algo_stats["max"], num_bytes)
            algo_to_byte_size[algo_name] = num_bytes
            print(f"  {algo_name} used {num_bytes} bytes")
        for algo_name, _ in algos:
            if algo_to_byte_size[algo_name] == min_bytes_this_img:
                summary_data[algo_name]["wins"] += 1

    print("\n**SUMMARY**")
    print(f"Number of images tested: {num_images}")
    for algo_name in summary_data:
        print(f"{algo_name}:")
        stats = summary_data[algo_name]
        bytes_sum = stats["sum"]
        bytes_avg = ceil(bytes_sum / num_images)
        print(
            f"  wins: {stats['wins']} total bytes used: {bytes_sum} avg: {bytes_avg} min: {stats['min']} max: {stats['max']}"
        )


if __name__ == "__main__":
    test_whole_suite()
