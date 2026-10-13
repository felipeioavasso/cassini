import requests

URL = "https://opus.pds-rings.seti.org/opus/api/fields.json"

response = requests.get(URL, timeout=30)
response.raise_for_status()

data = response.json()

# Procurar campos que possam indicar posição/centro
terms = [
    "center",
    "centroid",
    "sample",
    "line",
    "pixel",
    "coordinate",
]

text = response.text.lower()

print("Status:", response.status_code)
print()

for term in terms:
    print(
        f"{term:<12}:",
        text.count(term),
    )

print()
print("=" * 100)
print("CAMPOS RELACIONADOS")
print("=" * 100)

# A estrutura desse endpoint pode variar.
# Por enquanto imprimimos entradas que mencionam
# termos relevantes.
def search(obj, path=""):
    if isinstance(obj, dict):
        combined = " ".join(
            str(v)
            for v in obj.values()
            if isinstance(v, (str, int, float))
        ).lower()

        if any(term in combined for term in terms):
            print()
            print(path)
            print(obj)

        for key, value in obj.items():
            search(value, f"{path}/{key}")

    elif isinstance(obj, list):
        for index, value in enumerate(obj):
            search(value, f"{path}/{index}")


search(data)