from datetime import datetime

import requests

URL = "https://opus.pds-rings.seti.org/opus/api/data.json"

START_TIME = "2004-07-01T00:00:00"
END_TIME = "2017-09-15T23:59:59"

PAGE_SIZE = 10000


def fetch_all_observations():
    all_rows = []
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

        print(f"Buscando a partir da observação {startobs}...")

        response = requests.get(
            URL,
            params=params,
            timeout=90,
        )

        response.raise_for_status()

        data = response.json()

        rows = data.get("page", [])
        available = data.get("available", 0)

        all_rows.extend(rows)

        print(
            f"Recebidas: {len(rows)} | "
            f"Total acumulado: {len(all_rows)} / {available}"
        )

        if not rows:
            break

        if len(all_rows) >= available:
            break

        startobs += len(rows)

    return all_rows


def parse_observations(rows):
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

    return observations


def find_rgb_sequences(observations):
    sequences = []

    for i in range(len(observations) - 2):
        blue = observations[i]
        green = observations[i + 1]
        red = observations[i + 2]

        if blue["camera"] != "Wide Angle":
            continue

        if green["camera"] != "Wide Angle":
            continue

        if red["camera"] != "Wide Angle":
            continue

        filters = [
            blue["filter"],
            green["filter"],
            red["filter"],
        ]

        if filters != ["BL1", "GRN", "RED"]:
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


def main():
    rows = fetch_all_observations()

    print()
    print("=" * 100)
    print("TOTAL DE OBSERVAÇÕES:", len(rows))

    observations = parse_observations(rows)

    sequences = find_rgb_sequences(observations)

    print()
    print("=" * 100)
    print("SEQUÊNCIAS RGB WAC ENCONTRADAS:", len(sequences))
    print()

    for n, sequence in enumerate(sequences, start=1):
        print("=" * 100)

        print(
            f"SEQUÊNCIA {n} "
            f"({sequence['duration']:.1f} s)"
        )

        for channel in ["blue", "green", "red"]:
            obs = sequence[channel]

            print(
                f"{channel.upper():5} "
                f"{obs['time']}  "
                f"{obs['opus_id']}  "
                f"{obs['camera']}"
            )


if __name__ == "__main__":
    main()