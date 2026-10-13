from pathlib import Path  # noqa: I001

import requests


PROJECT_ROOT = Path(__file__).resolve().parents[1]

DEST = (
    PROJECT_ROOT
    / "data"
    / "spice"
    / "cassini"
)

DEST.mkdir(
    parents=True,
    exist_ok=True,
)


KERNELS = {
    # Leap seconds
    "naif0012.tls":
        "https://naif.jpl.nasa.gov/pub/naif/CASSINI/kernels/lsk/naif0012.tls",

    # Cassini spacecraft clock
    "cas00136.tsc":
        "https://naif.jpl.nasa.gov/pub/naif/CASSINI/kernels/sclk/cas00136.tsc",

    # Frames da Cassini e instrumentos
    "cas_v40.tf":
        "https://naif.jpl.nasa.gov/pub/naif/CASSINI/kernels/fk/cas_v40.tf",

    # Geometria da câmera ISS
    "cas_iss_v10.ti":
        "https://naif.jpl.nasa.gov/pub/naif/CASSINI/kernels/ik/cas_iss_v10.ti",

    # Posição da Cassini no período da imagem
    "091015AP_SCPSE_09284_09310.bsp":
        (
            "https://naif.jpl.nasa.gov/pub/naif/CASSINI/kernels/spk/"
            "091015AP_SCPSE_09284_09310.bsp"
        ),
    "09286_09291ra.bc":
    (
        "https://naif.jpl.nasa.gov/pub/naif/CASSINI/kernels/ck/"
        "09286_09291ra.bc"
    ),
    "pck00010.tpc":
    (
        "https://naif.jpl.nasa.gov/pub/naif/generic_kernels/pck/"
        "pck00010.tpc"
    ),
    "sat382-rocks-merge.bsp":
    (
        "https://naif.jpl.nasa.gov/pub/naif/"
        "generic_kernels/spk/satellites/a_old_versions/"
        "sat382-rocks-merge.bsp"
    ),
}


def download(url, destination):
    if destination.exists():
        print(
            f"Já existe: {destination.name}"
        )
        return

    print(
        f"Baixando: {destination.name}"
    )

    with requests.get(
        url,
        stream=True,
        timeout=120,
    ) as response:

        response.raise_for_status()

        with destination.open("wb") as file:

            for chunk in response.iter_content(
                chunk_size=1024 * 1024
            ):
                if chunk:
                    file.write(chunk)

    print(
        f"OK: {destination.name}"
    )


def main():
    print()
    print("=" * 80)
    print("SPICE — CASSINI")
    print("=" * 80)

    for filename, url in KERNELS.items():
        download(
            url,
            DEST / filename,
        )

    print()
    print("Kernels preparados em:")
    print(DEST)


if __name__ == "__main__":
    main()