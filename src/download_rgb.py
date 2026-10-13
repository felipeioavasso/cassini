from pathlib import Path

import requests

BASE_URL = (
    "https://opus.pds-rings.seti.org/holdings/"
    "calibrated/COISS_2xxx/COISS_2024/"
    "data/1534497821_1534811216/"
)

PROJECT_ROOT = Path(__file__).resolve().parents[1]

FILES = {
    "blue": [
        "W1534634233_1_CALIB.IMG",
        "W1534634233_1_CALIB.LBL",
    ],
    "green": [
        "W1534634266_1_CALIB.IMG",
        "W1534634266_1_CALIB.LBL",
    ],
    "red": [
        "W1534634299_1_CALIB.IMG",
        "W1534634299_1_CALIB.LBL",
    ],
}


def download_file(url: str, destination: Path) -> None:
    destination.parent.mkdir(parents=True, exist_ok=True)

    if destination.exists():
        print(f"Já existe: {destination.name}")
        return

    print(f"Baixando: {destination.name}")

    with requests.get(url, stream=True, timeout=60) as response:
        response.raise_for_status()

        with open(destination, "wb") as file:
            for chunk in response.iter_content(chunk_size=1024 * 1024):
                if chunk:
                    file.write(chunk)

    print(f"OK: {destination}")


def main() -> None:
    base_dir = PROJECT_ROOT / "data" / "raw" / "saturn_rgb"

    for channel, filenames in FILES.items():
        channel_dir = base_dir / channel

        for filename in filenames:
            url = BASE_URL + filename
            destination = channel_dir / filename

            download_file(url, destination)


if __name__ == "__main__":
    main()