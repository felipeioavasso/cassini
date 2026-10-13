import requests

BASE = (
    "https://opus.pds-rings.seti.org/holdings/"
    "calibrated/COISS_2xxx/COISS_2024/"
    "data/1534497821_1534811216/"
)

files = {
    "BLUE_IMG": "W1534634233_1_CALIB.IMG",
    "BLUE_LBL": "W1534634233_1_CALIB.LBL",

    "GREEN_IMG": "W1534634266_1_CALIB.IMG",
    "GREEN_LBL": "W1534634266_1_CALIB.LBL",

    "RED_IMG": "W1534634299_1_CALIB.IMG",
    "RED_LBL": "W1534634299_1_CALIB.LBL",
}


def format_size(size):
    if size is None:
        return "não informado"

    mb = size / (1024 * 1024)

    if mb >= 1:
        return f"{mb:.2f} MB"

    return f"{size / 1024:.2f} KB"


total = 0


for name, filename in files.items():

    url = BASE + filename

    response = requests.head(
        url,
        allow_redirects=True,
        timeout=30,
    )

    size = response.headers.get("Content-Length")
    size = int(size) if size else None

    print(
        f"{name:<12} "
        f"{response.status_code}  "
        f"{format_size(size)}"
    )

    if size:
        total += size


print()
print("-" * 40)
print(f"TOTAL: {format_size(total)}")