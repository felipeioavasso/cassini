from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np

PROJECT_ROOT = Path(__file__).resolve().parents[1]

FILES = {
    "BLUE": PROJECT_ROOT
    / "data/raw/saturn_rgb/blue/W1534634233_1_CALIB.IMG",

    "GREEN": PROJECT_ROOT
    / "data/raw/saturn_rgb/green/W1534634266_1_CALIB.IMG",

    "RED": PROJECT_ROOT
    / "data/raw/saturn_rgb/red/W1534634299_1_CALIB.IMG",
}

WIDTH = 1024
HEIGHT = 1024
HEADER_BYTES = 4096


def load_image(path: Path) -> np.ndarray:

    image = np.fromfile(
        path,
        dtype="<f4",
        offset=HEADER_BYTES,
        count=WIDTH * HEIGHT,
    )

    image = image.reshape(
        HEIGHT,
        WIDTH,
    )

    return image


def clean_image(image: np.ndarray) -> np.ndarray:

    image = image.astype(np.float64)

    # Remove NaN / infinito
    image[~np.isfinite(image)] = np.nan

    # Valores absurdamente grandes são pixels especiais/inválidos.
    # Para uma imagem calibrada em I/F não são valores físicos úteis.
    image[np.abs(image) > 100] = np.nan

    return image


for channel, path in FILES.items():

    image = load_image(path)
    image = clean_image(image)

    valid_pixels = image[np.isfinite(image)]

    print()
    print("=" * 60)
    print(channel)
    print("=" * 60)

    print("Shape:", image.shape)
    print("dtype:", image.dtype)

    print("Pixels válidos:", valid_pixels.size)
    print("Pixels inválidos:", image.size - valid_pixels.size)

    print("Min válido:", np.min(valid_pixels))
    print("Max válido:", np.max(valid_pixels))
    print("Média:", np.mean(valid_pixels))
    print("Mediana:", np.median(valid_pixels))

    print("P1:", np.percentile(valid_pixels, 1))
    print("P99:", np.percentile(valid_pixels, 99))
    print("P99.5:", np.percentile(valid_pixels, 99.5))

    vmin = np.percentile(valid_pixels, 1)
    vmax = np.percentile(valid_pixels, 99.5)

    plt.figure(figsize=(8, 8))

    plt.imshow(
        image,
        cmap="gray",
        vmin=vmin,
        vmax=vmax,
    )

    plt.title(f"Cassini ISS WAC — {channel}")

    plt.axis("off")
    plt.tight_layout()

    plt.show()