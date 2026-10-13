from pathlib import Path

import requests

PROJECT_ROOT = Path(__file__).resolve().parents[1]

OUTPUT_DIR = (
    PROJECT_ROOT
    / "outputs"
    / "images"
    / "saturn_candidates"
)

OUTPUT_DIR.mkdir(
    parents=True,
    exist_ok=True,
)


SEQUENCES = {
    1: "co-iss-n1520936977",
    2: "co-iss-w1521203375",
    3: "co-iss-w1521216142",
    4: "co-iss-w1527150321",
    5: "co-iss-w1527153921",
    6: "co-iss-w1527157521",
    7: "co-iss-w1527161121",
    8: "co-iss-w1532601393",
    9: "co-iss-w1532602086",
    10: "co-iss-w1532612193",
}


BASE_API = (
    "https://opus.pds-rings.seti.org/"
    "opus/api/files"
)


for number, opus_id in SEQUENCES.items():

    print()
    print("=" * 70)
    print(f"Sequência {number}: {opus_id}")

    response = requests.get(
        f"{BASE_API}/{opus_id}.json",
        timeout=30,
    )

    response.raise_for_status()

    data = response.json()

    files = data["data"][opus_id]

    # Thumbnail pequeno do OPUS
    urls = files.get("browse_small")

    if not urls:
        print("Sem browse_small.")
        continue

    url = urls[0]

    destination = (
        OUTPUT_DIR
        / f"sequence_{number:02d}_{opus_id}.jpg"
    )

    print("Preview:", url)

    image_response = requests.get(
        url,
        timeout=30,
    )

    image_response.raise_for_status()

    destination.write_bytes(
        image_response.content
    )

    size_kb = (
        len(image_response.content)
        / 1024
    )

    print(
        f"Salvo: {destination.name} "
        f"({size_kb:.1f} KB)"
    )


print()
print("=" * 70)
print("Previews salvos em:")
print(OUTPUT_DIR)