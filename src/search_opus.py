import requests

BASE_URL = "https://opus.pds-rings.seti.org/opus/api/files"

observacoes = {
    "BLUE": "co-iss-w1534634233",
    "GREEN": "co-iss-w1534634266",
    "RED": "co-iss-w1534634299",
}


for canal, opus_id in observacoes.items():

    print("\n" + "=" * 100)
    print(f"{canal}: {opus_id}")
    print("=" * 100)

    url = f"{BASE_URL}/{opus_id}.json"

    response = requests.get(
        url,
        timeout=30,
    )

    print("Status:", response.status_code)
    print("URL:", response.url)

    if response.status_code != 200:
        print(response.text[:500])
        continue

    data = response.json()

    print(data)