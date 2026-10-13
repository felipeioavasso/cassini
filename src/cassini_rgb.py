from pathlib import Path  # noqa: I001
import argparse

import matplotlib.pyplot as plt
import numpy as np
import requests


PROJECT_ROOT = Path(__file__).resolve().parents[1]

FILES_API = "https://opus.pds-rings.seti.org/opus/api/files"

WIDTH = 1024
HEIGHT = 1024
HEADER_BYTES = 4096


def parse_args():
    parser = argparse.ArgumentParser(
        description="Reconstrói imagens RGB da Cassini ISS."
    )

    parser.add_argument("--name", required=True)
    parser.add_argument("--blue", required=True)
    parser.add_argument("--green", required=True)
    parser.add_argument("--red", required=True)

    return parser.parse_args()


def get_calibrated_files(opus_id):
    url = f"{FILES_API}/{opus_id}.json"

    response = requests.get(
        url,
        timeout=30,
    )

    response.raise_for_status()

    data = response.json()

    files = data["data"][opus_id]

    calibrated = files.get("coiss_calib")

    if not calibrated:
        raise RuntimeError(
            f"Produto calibrado não encontrado: {opus_id}"
        )

    return calibrated


def download_file(url, destination):
    destination.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    if destination.exists():
        print(f"Já existe: {destination.name}")
        return

    print(f"Baixando: {destination.name}")

    with requests.get(
        url,
        stream=True,
        timeout=60,
    ) as response:

        response.raise_for_status()

        with destination.open("wb") as file:

            for chunk in response.iter_content(
                chunk_size=1024 * 1024
            ):
                if chunk:
                    file.write(chunk)


def download_channel(sequence_dir, channel, opus_id):
    channel_dir = sequence_dir / channel

    urls = get_calibrated_files(opus_id)

    for url in urls:
        filename = url.split("/")[-1]

        download_file(
            url,
            channel_dir / filename,
        )


def find_image(sequence_dir, channel):
    files = list(
        (sequence_dir / channel).glob("*_CALIB.IMG")
    )

    if len(files) != 1:
        raise RuntimeError(
            f"{channel}: esperado 1 IMG, "
            f"encontrado(s) {len(files)}."
        )

    return files[0]


def load_image(path):
    image = np.fromfile(
        path,
        dtype="<f4",
        offset=HEADER_BYTES,
        count=WIDTH * HEIGHT,
    )

    image = image.reshape(
        HEIGHT,
        WIDTH,
    ).astype(np.float64)

    image[~np.isfinite(image)] = np.nan
    image[np.abs(image) > 100] = np.nan

    return image


def prepare_for_alignment(image):
    clean = np.nan_to_num(
        image,
        nan=0.0,
    )

    low = np.percentile(clean, 5)
    high = np.percentile(clean, 99)

    clean = np.clip(
        clean,
        low,
        high,
    )

    return clean - clean.mean()


def find_shift(reference, moving, max_shift=20):
    ref = prepare_for_alignment(reference)
    mov = prepare_for_alignment(moving)

    best_score = -np.inf
    best_shift = (0, 0)

    for dy in range(
        -max_shift,
        max_shift + 1,
    ):
        for dx in range(
            -max_shift,
            max_shift + 1,
        ):
            shifted = np.roll(
                mov,
                shift=(dy, dx),
                axis=(0, 1),
            )

            score = np.sum(
                ref * shifted
            )

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
        dst_x1:dst_x2,
    ] = image[
        src_y1:src_y2,
        src_x1:src_x2,
    ]

    return shifted


def build_rgb(red, green, blue):
    stack = np.dstack([
        red,
        green,
        blue,
    ])

    valid = stack[
        np.isfinite(stack)
    ]

    low = np.percentile(
        valid,
        0.5,
    )

    high = np.percentile(
        valid,
        99.7,
    )

    rgb = (
        stack - low
    ) / (
        high - low
    )

    rgb = np.clip(
        rgb,
        0,
        1,
    )

    return np.nan_to_num(rgb)


def save_rgb(rgb, output, name):
    output.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    plt.figure(
        figsize=(10, 10)
    )

    plt.imshow(rgb)

    plt.title(
        f"{name}\nCassini ISS — RED + GRN + BL1"
    )

    plt.axis("off")
    plt.tight_layout()

    plt.savefig(
        output,
        dpi=200,
        bbox_inches="tight",
    )

    plt.close()


def main():
    args = parse_args()

    sequence_dir = (
        PROJECT_ROOT
        / "data"
        / "raw"
        / args.name
    )

    observations = {
        "blue": args.blue,
        "green": args.green,
        "red": args.red,
    }

    print()
    print("=" * 80)
    print("CASSINI RGB")
    print("=" * 80)

    for channel, opus_id in observations.items():

        print()
        print(
            f"{channel.upper()}: "
            f"{opus_id}"
        )

        download_channel(
            sequence_dir,
            channel,
            opus_id,
        )

    blue_path = find_image(
        sequence_dir,
        "blue",
    )

    green_path = find_image(
        sequence_dir,
        "green",
    )

    red_path = find_image(
        sequence_dir,
        "red",
    )

    blue = load_image(blue_path)
    green = load_image(green_path)
    red = load_image(red_path)

    print()
    print("Calculando alinhamento...")

    shift_blue = find_shift(
        green,
        blue,
    )

    shift_red = find_shift(
        green,
        red,
    )

    print(
        "BLUE:",
        shift_blue,
    )

    print(
        "GREEN:",
        (0, 0),
    )

    print(
        "RED:",
        shift_red,
    )

    blue = apply_shift(
        blue,
        shift_blue,
    )

    red = apply_shift(
        red,
        shift_red,
    )

    rgb = build_rgb(
        red,
        green,
        blue,
    )

    rgb_enhanced = enhance_rgb(rgb)


    output = (
        PROJECT_ROOT
        / "outputs"
        / "images"
        / f"{args.name}_rgb.png"
    )

    save_rgb(
        rgb,
        output,
        args.name,
    )

    output_enhanced = (
        PROJECT_ROOT
        / "outputs"
        / "images"
        / f"{args.name}_rgb_enhanced.png"
    )

    save_rgb(
        rgb_enhanced,
        output_enhanced,
        f"{args.name} — Enhanced",
    )

    print()
    print("Imagem salva em:")
    print(output)

def enhance_rgb(rgb):
    image = rgb.copy()

    gamma = 0.75
    image = np.power(image, gamma)

    black = 0.003
    white = 0.95

    image = (image - black) / (white - black)
    image = np.clip(image, 0, 1)

    gray = (
        0.2126 * image[:, :, 0]
        + 0.7152 * image[:, :, 1]
        + 0.0722 * image[:, :, 2]
    )

    gray = gray[:, :, np.newaxis]

    saturation = 1.10

    image = gray + saturation * (image - gray)

    return np.clip(image, 0, 1)




if __name__ == "__main__":
    main()