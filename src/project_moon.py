from pathlib import Path

import numpy as np
import spiceypy as spice

PROJECT_ROOT = Path(__file__).resolve().parents[1]

SPICE_DIR = (
    PROJECT_ROOT
    / "data"
    / "spice"
    / "cassini"
)

UTC = "2009-10-17T05:21:00.048"

TARGET = "ENCELADUS"

# Cassini ISS Wide Angle Camera
CAMERA_FRAME = "CASSINI_ISS_WAC"
CAMERA_ID = -82361


def load_kernels():
    kernels = [
        "naif0012.tls",
        "cas00136.tsc",
        "pck00010.tpc",
        "cas_v40.tf",
        "cas_iss_v10.ti",
        "091015AP_SCPSE_09284_09310.bsp",
        "09286_09291ra.bc",
    ]

    for kernel in kernels:
        path = SPICE_DIR / kernel

        if not path.exists():
            raise FileNotFoundError(
                f"Kernel não encontrado: {path}"
            )

        spice.furnsh(str(path))

        print("OK:", kernel)


def main():
    try:
        load_kernels()

        et = spice.str2et(UTC)

        print()
        print("=" * 80)
        print("OBSERVAÇÃO")
        print("=" * 80)

        print("UTC:", UTC)
        print("ET :", et)

        # --------------------------------------------------
        # 1. Posição de Encélado vista da Cassini
        # diretamente no frame da câmera
        # --------------------------------------------------

        position, light_time = spice.spkpos(  # noqa: RUF059
            TARGET,
            et,
            CAMERA_FRAME,
            "LT+S",
            "CASSINI",
        )

        distance = spice.vnorm(position)

        direction = position / distance

        print()
        print("=" * 80)
        print("ENCELADUS NO FRAME DA WAC")
        print("=" * 80)

        print("Vetor:")
        print(position)

        print()
        print("Direção normalizada:")
        print(direction)

        print()
        print(
            f"Distância: {distance:,.2f} km"
        )

        # --------------------------------------------------
        # 2. Campo de visão da câmera
        # --------------------------------------------------

        (
            shape,
            frame,
            boresight,
            bounds,
        ) = spice.getfov(
            CAMERA_ID,
            4,
        )

        print()
        print("=" * 80)
        print("CAMPO DE VISÃO")
        print("=" * 80)

        print("Shape:", shape)
        print("Frame:", frame)

        print()
        print("Boresight:")
        print(boresight)

        print()
        print("Limites:")

        for bound in bounds:
            print(bound)

        # --------------------------------------------------
        # 3. Coordenadas angulares aproximadas
        #
        # No frame da câmera, o boresight normalmente
        # aponta aproximadamente no eixo +Z.
        # --------------------------------------------------

        x = direction[0]
        y = direction[1]
        z = direction[2]

        angle_x = np.degrees(
            np.arctan2(x, z)
        )

        angle_y = np.degrees(
            np.arctan2(y, z)
        )

        print()
        print("=" * 80)
        print("POSIÇÃO ANGULAR")
        print("=" * 80)

        print(
            f"Horizontal: {angle_x:.6f}°"
        )

        print(
            f"Vertical:   {angle_y:.6f}°"
        )

        # --------------------------------------------------
        # 4. Teste oficial: está dentro do FOV?
        # --------------------------------------------------

        visible = spice.fovtrg(
            "CASSINI_ISS_WAC",
            TARGET,
            "POINT",
            "",
            "LT+S",
            "CASSINI",
            et,
        )

        print()
        print("=" * 80)
        print("VISIBILIDADE")
        print("=" * 80)

        print(
            f"{TARGET} dentro do FOV:",
            visible,
        )

    finally:
        spice.kclear()


if __name__ == "__main__":
    main()