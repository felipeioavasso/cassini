from pathlib import Path

import requests

PROJECT_ROOT = Path(__file__).resolve().parents[1]

FILES_API = "https://opus.pds-rings.seti.org/opus/api/files"

SEQUENCE_NAME = "saturn_2008_01_02"

OBSERVATIONS = {
    "blue": "co-iss-w1577981266",
    "green": "co-iss-w1577981299",
    "red": "co-iss-w1577981332",
}


def get_calibrated_files(opus_id: str):
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
            f"Nenhum produto calibrado encontrado para {opus_id}"
        )

    return calibrated


def download_file(url: str, destination: Path):
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

    print(f"OK: {destination}")


def main():
    base_dir = (
        PROJECT_ROOT
        / "data"
        / "raw"
        / SEQUENCE_NAME
    )

    for channel, opus_id in OBSERVATIONS.items():

        print()
        print("=" * 80)
        print(channel.upper())
        print(opus_id)
        print("=" * 80)

        calibrated_files = get_calibrated_files(
            opus_id
        )

        for url in calibrated_files:

            filename = url.split("/")[-1]

            destination = (
                base_dir
                / channel
                / filename
            )

            download_file(
                url,
                destination,
            )


if __name__ == "__main__":
    main()