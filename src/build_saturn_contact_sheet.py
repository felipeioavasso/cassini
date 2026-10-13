from datetime import datetime, timedelta
from io import BytesIO
from pathlib import Path

import matplotlib.pyplot as plt
import requests
from PIL import Image

PROJECT_ROOT = Path(__file__).resolve().parents[1]

OUTPUT_DIR = (
    PROJECT_ROOT
    / "outputs"
    / "images"
    / "saturn_contact_sheet"
)

PREVIEW_DIR = OUTPUT_DIR / "previews"

OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
PREVIEW_DIR.mkdir(parents=True, exist_ok=True)


URL = "https://opus.pds-rings.seti.org/opus/api/data.json"
FILES_API = "https://opus.pds-rings.seti.org/opus/api/files"

START_TIME = "2004-07-01T00:00:00"
END_TIME = "2017-09-15T23:59:59"

PAGE_SIZE = 10000

# Aproximadamente uma candidata a cada 60 dias
MIN_DAYS_BETWEEN = 60


def fetch_all_observations():
    rows = []
    startobs = 1

    while True:
        params = {
            "instrument": "Cassini ISS",
            "target": "Saturn",
            "time1": START_TIME,
            "time2": END_TIME,
            "cols": (
                "opusid,"
                "time1,"
                "COISScamera,"
                "COISSfilter"
            ),
            "order": "time1",
            "limit": PAGE_SIZE,
            "startobs": startobs,
        }

        print(f"Consultando OPUS: {startobs}...")

        response = requests.get(
            URL,
            params=params,
            timeout=90,
        )

        response.raise_for_status()

        data = response.json()

        page = data.get("page", [])
        available = data.get("available", 0)

        rows.extend(page)

        print(
            f"Acumulado: {len(rows)} / {available}"
        )

        if not page:
            break

        if len(rows) >= available:
            break

        startobs += len(page)

    return rows


def find_rgb_sequences(rows):
    observations = []

    for row in rows:
        opus_id, time, camera, filter_name = row

        observations.append(
            {
                "opus_id": opus_id,
                "time": datetime.fromisoformat(time),
                "camera": camera,
                "filter": filter_name,
            }
        )

    sequences = []

    for i in range(len(observations) - 2):
        blue = observations[i]
        green = observations[i + 1]
        red = observations[i + 2]

        if (
            blue["camera"] != "Wide Angle"
            or green["camera"] != "Wide Angle"
            or red["camera"] != "Wide Angle"
        ):
            continue

        if [
            blue["filter"],
            green["filter"],
            red["filter"],
        ] != ["BL1", "GRN", "RED"]:
            continue

        duration = (
            red["time"] - blue["time"]
        ).total_seconds()

        if duration > 180:
            continue

        sequences.append(
            {
                "blue": blue,
                "green": green,
                "red": red,
                "duration": duration,
            }
        )

    return sequences


def sample_sequences(sequences):
    selected = []

    last_date = None

    for sequence in sequences:
        date = sequence["green"]["time"]

        if last_date is None:
            selected.append(sequence)
            last_date = date
            continue

        if date - last_date >= timedelta(
            days=MIN_DAYS_BETWEEN
        ):
            selected.append(sequence)
            last_date = date

    return selected


def get_preview_url(opus_id):
    response = requests.get(
        f"{FILES_API}/{opus_id}.json",
        timeout=30,
    )

    response.raise_for_status()

    data = response.json()

    files = data["data"][opus_id]

    previews = (
        files.get("browse_small")
        or files.get("browse_medium")
        or files.get("browse_thumb")
    )

    if not previews:
        return None

    return previews[0]


def download_preview(number, sequence):
    opus_id = sequence["green"]["opus_id"]

    url = get_preview_url(opus_id)

    if not url:
        print(
            f"{number:02d}: sem preview"
        )
        return None

    response = requests.get(
        url,
        timeout=30,
    )

    response.raise_for_status()

    image = Image.open(
        BytesIO(response.content)
    ).convert("RGB")

    date = sequence["green"]["time"]

    filename = (
        f"{number:02d}_"
        f"{date:%Y-%m-%d}_"
        f"{opus_id}.jpg"
    )

    path = PREVIEW_DIR / filename

    image.save(
        path,
        quality=90,
    )

    print(
        f"{number:02d} | "
        f"{date:%Y-%m-%d} | "
        f"{opus_id}"
    )

    return {
        "number": number,
        "image": image,
        "date": date,
        "opus_id": opus_id,
        "sequence": sequence,
    }


def build_contact_sheet(items):
    cols = 5

    rows = (
        len(items) + cols - 1
    ) // cols

    fig = plt.figure(
        figsize=(15, rows * 3.2)
    )

    for index, item in enumerate(
        items,
        start=1,
    ):
        ax = fig.add_subplot(
            rows,
            cols,
            index,
        )

        ax.imshow(item["image"])

        ax.set_title(
            (
                f"#{item['number']:02d}\n"
                f"{item['date']:%d/%m/%Y}"
            ),
            fontsize=9,
        )

        ax.axis("off")

    plt.tight_layout()

    output = (
        OUTPUT_DIR
        / "saturn_rgb_candidates.jpg"
    )

    plt.savefig(
        output,
        dpi=150,
        bbox_inches="tight",
    )

    plt.close()

    return output


def save_catalog(items):
    output = (
        OUTPUT_DIR
        / "saturn_rgb_candidates.txt"
    )

    with output.open(
        "w",
        encoding="utf-8",
    ) as file:
        for item in items:
            sequence = item["sequence"]

            file.write(
                f"#{item['number']:02d}\n"
            )

            file.write(
                f"Data: "
                f"{item['date']:%Y-%m-%d}\n"
            )

            file.write(
                f"BLUE: "
                f"{sequence['blue']['opus_id']}\n"
            )

            file.write(
                f"GREEN: "
                f"{sequence['green']['opus_id']}\n"
            )

            file.write(
                f"RED: "
                f"{sequence['red']['opus_id']}\n"
            )

            file.write("\n")

    return output


def main():
    rows = fetch_all_observations()

    sequences = find_rgb_sequences(rows)

    print()
    print(
        "Sequências RGB encontradas:",
        len(sequences),
    )

    selected = sample_sequences(
        sequences
    )

    print(
        "Selecionadas para preview:",
        len(selected),
    )

    print()
    print("Baixando previews...")
    print()

    items = []

    for number, sequence in enumerate(
        selected,
        start=1,
    ):
        item = download_preview(
            number,
            sequence,
        )

        if item:
            items.append(item)

    print()

    contact_sheet = build_contact_sheet(
        items
    )

    catalog = save_catalog(
        items
    )

    print("=" * 70)
    print("Contact sheet:")
    print(contact_sheet)

    print()
    print("Catálogo:")
    print(catalog)


if __name__ == "__main__":
    main()