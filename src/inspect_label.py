from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]

labels = {
    "BLUE": PROJECT_ROOT
    / "data"
    / "raw"
    / "saturn_rgb"
    / "blue"
    / "W1534634233_1_CALIB.LBL",

    "GREEN": PROJECT_ROOT
    / "data"
    / "raw"
    / "saturn_rgb"
    / "green"
    / "W1534634266_1_CALIB.LBL",

    "RED": PROJECT_ROOT
    / "data"
    / "raw"
    / "saturn_rgb"
    / "red"
    / "W1534634299_1_CALIB.LBL",
}


for channel, path in labels.items():
    print()
    print("=" * 80)
    print(channel)
    print("=" * 80)

    content = path.read_text(
        encoding="latin-1",
        errors="replace",
    )

    print(content)