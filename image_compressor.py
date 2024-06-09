from sys import argv
from math import ceil
from PIL import Image

def png_to_bit_array(png_file):
    # Open the PNG image
    img = Image.open(png_file)

    # Convert the image to grayscale if it's not already
    img = img.convert('L')

    # Get pixel data as a byte array
    pixel_data = img.tobytes()

    return list(map(lambda b: 1 if b else 0, pixel_data))


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
    

if __name__ == "__main__":
    png_file = argv[1]
    # print(calculate_pairwise_encoding(([0] * 3 + [1] * 7) * 2, 2, 3))
    print(calculate_pairwise_encoding([0, 0, 0, 0, 1], 2, 2))
    print(calculate_bit_prefix_encoding([0, 0, 0, 0, 1], 2))
    bit_array = png_to_bit_array(png_file)
    # print(bit_array)
    # print(len(bit_array))
    # print(len(set(bit_array)))
    best_pairwise_size = 512
    best_pairwise_num_bits = (None, None)
    best_pairwise_encoded = None
    pairwise_sizes = []
    for i in range(1, 13):
        i_sizes = []
        for j in range(1, 13):
            num_bytes, encoded = calculate_pairwise_encoding(bit_array, i, j)
            if num_bytes < best_pairwise_size:
                best_pairwise_size = num_bytes
                best_pairwise_num_bits = (i, j)
                best_pairwise_encoded = encoded
            i_sizes.append(str(len(encoded)))
        pairwise_sizes.append(i_sizes)
    # print("\n".join(map(lambda i_sizes: ','.join(i_sizes), pairwise_sizes)))
    print(f"best pairwise size: {best_pairwise_size} (zero len {best_pairwise_num_bits[0]}, one len {best_pairwise_num_bits[1]})")
    # print(best_pairwise_num_bits)
    # print(best_pairwise_encoded)
    # print(len([b for b in best_pairwise_encoded if b == 0]))

    best_bit_prefix_size = 512
    best_bit_prefix_num_bits = None
    best_bit_prefix_encoded = None
    for i in range(1, 13):
        num_bytes, encoded = calculate_bit_prefix_encoding(bit_array, i)
        if num_bytes < best_bit_prefix_size:
            best_bit_prefix_size = num_bytes
            best_bit_prefix_num_bits = i
            best_bit_prefix_encoded = encoded
    print(f"best bit prefix size: {best_bit_prefix_size} ({best_bit_prefix_num_bits} bit len)")
    # print(best_bit_prefix_num_bits)


