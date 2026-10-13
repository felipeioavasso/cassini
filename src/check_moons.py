import requests

URL = "https://opus.pds-rings.seti.org/opus/api/data.json"

OPUS_ID = "co-iss-w1634450629"


def get_targets():
    params = {
        "opusid": OPUS_ID,
        "cols": (
            "opusid,"
            "time1,"
            "surfacegeometrytargetlist"
        ),
        "limit": 1,
    }

    response = requests.get(
        URL,
        params=params,
        timeout=30,
    )

    response.raise_for_status()

    data = response.json()

    labels = data["labels"]
    row = data["page"][0]

    result = dict(zip(labels, row))

    target_list = result.get(
        "Multiple Target List",
        ""
    )

    targets = [
        target.strip()
        for target in target_list.split(",")
        if target.strip()
    ]

    return result, targets


def make_slug(name):
    return (
        name
        .lower()
        .replace(" ", "")
        .replace("-", "")
    )


def get_coordinates(targets):
    cols = [
        "opusid",
        "time1",
        "surfacegeometrytargetlist",
    ]

    target_info = {}

    for target in targets:
        slug = make_slug(target)

        x_field = (
            f"SURFACEGEO{slug}_centerxcoordinate"
        )

        y_field = (
            f"SURFACEGEO{slug}_centerycoordinate"
        )

        cols.extend([
            x_field,
            y_field,
        ])

        target_info[target] = {
            "slug": slug,
        }

    params = {
        "opusid": OPUS_ID,
        "cols": ",".join(cols),
        "limit": 1,
    }

    response = requests.get(
        URL,
        params=params,
        timeout=30,
    )

    response.raise_for_status()

    data = response.json()

    result = dict(
        zip(
            data["labels"],
            data["page"][0],
        )
    )

    for target in targets:
        target_info[target]["x"] = result.get(
            f"Center X Coordinate [{target}]"
        )

        target_info[target]["y"] = result.get(
            f"Center Y Coordinate [{target}]"
        )

    return target_info


def needs_spice(value):
    return value in {
        None,
        "",
        "N/A",
        "NULL",
        "None",
    }


def main():
    base_info, targets = get_targets()

    print()
    print("=" * 90)
    print("CORPOS NO CAMPO")
    print("=" * 90)

    print(
        "Data:",
        base_info["Observation Start Time (YMDhms)"]
    )

    print(
        "Corpos:",
        ", ".join(targets)
    )

    print()

    coordinates = get_coordinates(
        targets
    )

    spice_targets = []

    for target, info in coordinates.items():

        print(target.upper())
        print(" X:", info["x"])
        print(" Y:", info["y"])

        if (
            needs_spice(info["x"])
            or needs_spice(info["y"])
        ):
            print(" → fallback SPICE necessário")

            spice_targets.append(target)

        else:
            print(" → coordenadas disponíveis no OPUS")

        print()

    if spice_targets:
        print("=" * 90)
        print("FALLBACK SPICE")
        print("=" * 90)

        print(
            "Calcular via SPICE:",
            ", ".join(spice_targets)
        )


if __name__ == "__main__":
    main()