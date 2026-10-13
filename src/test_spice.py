from pathlib import Path

import spiceypy as spice

PROJECT_ROOT = Path(__file__).resolve().parents[1]

SPICE_DIR = (
    PROJECT_ROOT
    / "data"
    / "spice"
    / "cassini"
)


def load_kernels():
    kernels = [
        "naif0012.tls",
        "cas00136.tsc",
        "pck00010.tpc",
        "cas_v40.tf",
        "cas_iss_v10.ti",
        "091015AP_SCPSE_09284_09310.bsp",
        "sat382-rocks-merge.bsp",
        "09286_09291ra.bc",
    ]

    for kernel in kernels:
        path = SPICE_DIR / kernel

        if not path.exists():
            print("FALTANDO:", kernel)
            continue

        spice.furnsh(str(path))
        print("OK:", kernel)


def inspect_spks():
    print()
    print("=" * 80)
    print("OBJETOS PRESENTES NOS SPKs")
    print("=" * 80)

    for path in SPICE_DIR.glob("*.bsp"):
        print()
        print(path.name)

        ids = spice.spkobj(str(path))

        for object_id in ids:
            try:
                name = spice.bodc2n(int(object_id))
            except Exception:
                name = "DESCONHECIDO"

            print(
                f"  {int(object_id):>8}  {name}"
            )


def test_positions():
    utc = "2009-10-17T05:21:00.048"

    et = spice.str2et(utc)

    print()
    print("=" * 80)
    print("TESTE DE POSIÇÃO")
    print("=" * 80)
    print("UTC:", utc)
    print("ET :", et)
    print()

    targets = [
        "SATURN",
        "ENCELADUS",
        "PANDORA",
        "ANTHE",
    ]

    for target in targets:
        try:
            position, light_time = spice.spkpos(
                target,
                et,
                "J2000",
                "LT+S",
                "CASSINI",
            )

            distance = spice.vnorm(position)

            print(f"{target:<12} OK")
            print(
                f"  distância: {distance:,.2f} km"
            )
            print(
                f"  vetor: {position}"
            )

        except Exception as error:
            print(f"{target:<12} ERRO")
            print(
                " ",
                str(error).splitlines()[0],
            )

        print()


def main():
    try:
        load_kernels()

        inspect_spks()

        test_positions()

    finally:
        spice.kclear()


if __name__ == "__main__":
    main()