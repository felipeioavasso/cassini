from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np

PROJECT_ROOT = Path(__file__).resolve().parents[1]

SEQUENCE_DIR = (
    PROJECT_ROOT
    / "data"
    / "raw"
    / "saturn_2011_02_23"
)


def find_calibrated_img(channel):
    files = list(
        (SEQUENCE_DIR / channel).glob("*_CALIB.IMG")
    )

    if len(files) != 1:
        raise RuntimeError(
            f"Esperava 1 IMG em {channel}, "
            f"mas encontrei {len(files)}"
        )

    return files[0]


FILES = {
    "blue": find_calibrated_img("blue"),
    "green": find_calibrated_img("green"),
    "red": find_calibrated_img("red"),
}

WIDTH = 1024
HEIGHT = 1024
HEADER_BYTES = 4096

OUTPUT = (
    PROJECT_ROOT
    / "outputs"
    / "images"
    / "saturn_2011_02_23_rgb.png"
)


def load_image(path):
    image = np.fromfile(
        path,
        dtype="<f4",
        offset=HEADER_BYTES,
        count=WIDTH * HEIGHT,
    )

    image = image.reshape(HEIGHT, WIDTH)
    image = image.astype(np.float64)

    image[~np.isfinite(image)] = np.nan
    image[np.abs(image) > 100] = np.nan

    return image


def prepare_for_alignment(image):
    clean = np.nan_to_num(image, nan=0.0)

    low = np.percentile(clean, 5)
    high = np.percentile(clean, 99)

    clean = np.clip(clean, low, high)

    clean = clean - clean.mean()

    return clean


def find_shift(reference, moving, max_shift=20):
    ref = prepare_for_alignment(reference)
    mov = prepare_for_alignment(moving)

    best_score = -np.inf
    best_shift = (0, 0)

    for dy in range(-max_shift, max_shift + 1):
        for dx in range(-max_shift, max_shift + 1):

            shifted = np.roll(mov, shift=(dy, dx), axis=(0, 1))

            score = np.sum(ref * shifted)

            if score > best_score:
                best_score = score
                best_shift = (dy, dx)

    return best_shift


def apply_shift(image, shift):
    dy, dx = shift

    shifted = np.full_like(
        image,
        np.nan,
        dtype=np.float64,
    )

    height, width = image.shape

    src_y1 = max(0, -dy)
    src_y2 = min(height, height - dy)

    src_x1 = max(0, -dx)
    src_x2 = min(width, width - dx)

    dst_y1 = max(0, dy)
    dst_y2 = min(height, height + dy)

    dst_x1 = max(0, dx)
    dst_x2 = min(width, width + dx)

    shifted[
        dst_y1:dst_y2,
        dst_x1:dst_x2
    ] = image[
        src_y1:src_y2,
        src_x1:src_x2
    ]

    return shifted


def normalize_channel(image):
    valid = image[np.isfinite(image)]

    low = np.percentile(valid, 0.5)
    high = np.percentile(valid, 99.7)

    result = (image - low) / (high - low)

    result = np.clip(result, 0, 1)
    result = np.nan_to_num(result)

    return result


blue = load_image(FILES["blue"])
green = load_image(FILES["green"])
red = load_image(FILES["red"])

print()
print("Arquivos:")
print("BLUE :", FILES["blue"].name)
print("GREEN:", FILES["green"].name)
print("RED  :", FILES["red"].name)
print()

print("Calculando alinhamento...")

# Usamos o verde como referência
shift_blue = find_shift(green, blue)
shift_red = find_shift(green, red)

print("Deslocamento BLUE:", shift_blue)
print("Deslocamento GREEN:", (0, 0))
print("Deslocamento RED:", shift_red)

blue_aligned = apply_shift(blue, shift_blue)
red_aligned = apply_shift(red, shift_red)

stack = np.dstack([
    red_aligned,
    green,
    blue_aligned,
])

valid = stack[np.isfinite(stack)]

low = np.percentile(valid, 0.5)
high = np.percentile(valid, 99.7)

rgb = (stack - low) / (high - low)

rgb = np.clip(
    rgb,
    0,
    1,
)

rgb = np.nan_to_num(rgb)

OUTPUT.parent.mkdir(parents=True, exist_ok=True)

plt.figure(figsize=(10, 10))

plt.imshow(rgb)

plt.title(
    "Saturno — Cassini ISS WAC\n"
    "RED + GRN + BL1"
)

plt.axis("off")
plt.tight_layout()

plt.savefig(
    OUTPUT,
    dpi=200,
    bbox_inches="tight",
)

plt.show()

print()
print("Imagem salva em:")
print(OUTPUT)