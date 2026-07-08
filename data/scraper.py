# hotel data collector - OpenStreetMap (Nominatim + Overpass), no scraping/blocking issues
import csv
import os
import time
import requests

LOCATIONS = [
    "Nairobi", "Mombasa", "Diani", "Naivasha", "Nakuru",
    "Maasai Mara", "Amboseli", "Watamu", "Malindi", "Kisumu",
    "Nanyuki", "Lamu", "Zanzibar", "Arusha", "Kampala", "Dar es Salaam"
]

FIELDS = [
    "Hotel Name", "Location", "County or Region", "Country",
    "Hotel Description", "Price Range", "Amenities", "Room Types",
    "Rating", "Review Summary", "Nearby Attractions", "Hotel Category",
    "Contact Information", "Website URL", "Image URL", "Source URL"
]

COUNTRY_MAP = {
    "Nairobi": ("Nairobi County", "Kenya"),
    "Mombasa": ("Mombasa County", "Kenya"),
    "Diani": ("Kwale County", "Kenya"),
    "Naivasha": ("Nakuru County", "Kenya"),
    "Nakuru": ("Nakuru County", "Kenya"),
    "Maasai Mara": ("Narok County", "Kenya"),
    "Amboseli": ("Kajiado County", "Kenya"),
    "Watamu": ("Kilifi County", "Kenya"),
    "Malindi": ("Kilifi County", "Kenya"),
    "Kisumu": ("Kisumu County", "Kenya"),
    "Nanyuki": ("Laikipia County", "Kenya"),
    "Lamu": ("Lamu County", "Kenya"),
    "Zanzibar": ("Zanzibar", "Tanzania"),
    "Arusha": ("Arusha Region", "Tanzania"),
    "Kampala": ("Central Region", "Uganda"),
    "Dar es Salaam": ("Dar es Salaam Region", "Tanzania"),
}

# Nominatim requires a descriptive User-Agent identifying your app (their usage policy)
HEADERS = {"User-Agent": "TravelAfricaRAGProject/1.0 (student portfolio project)"}

NOMINATIM_URL = "https://nominatim.openstreetmap.org/search"
OVERPASS_URL = "https://overpass-api.de/api/interpreter"


def geocode_location(location):
    """Get (lat, lon) for a place name using Nominatim."""
    params = {"q": location, "format": "json", "limit": 1}
    resp = requests.get(NOMINATIM_URL, params=params, headers=HEADERS, timeout=20)
    resp.raise_for_status()
    results = resp.json()
    if not results:
        return None
    return float(results[0]["lat"]), float(results[0]["lon"])


def query_overpass_hotels(lat, lon, radius_m=15000, max_retries=4):
    """Query Overpass for tourism=hotel nodes/ways within radius_m of (lat, lon).

    Retries on 429 (rate limited) and 504 (server overloaded/timeout) with
    increasing wait times, since the free public Overpass server is shared
    and gets busy. Gives up after max_retries and returns [].
    """
    query = f"""
    [out:json][timeout:60];
    (
      node["tourism"="hotel"](around:{radius_m},{lat},{lon});
      way["tourism"="hotel"](around:{radius_m},{lat},{lon});
    );
    out center tags;
    """

    wait = 10  # seconds, doubles after each retry
    for attempt in range(1, max_retries + 1):
        resp = requests.post(OVERPASS_URL, data={"data": query}, headers=HEADERS, timeout=90)

        if resp.status_code == 200:
            return resp.json().get("elements", [])

        if resp.status_code in (429, 504):
            print(f"  Overpass busy ({resp.status_code}), retry {attempt}/{max_retries} in {wait}s...")
            time.sleep(wait)
            wait *= 2
            continue

        # Any other error (400 = bad query, etc.) - no point retrying
        print(f"Overpass error {resp.status_code}: {resp.text[:200]}")
        return []

    print(f"  Gave up after {max_retries} retries.")
    return []


def element_to_hotel(el, location):
    tags = el.get("tags", {})
    name = tags.get("name")
    if not name:
        return None

    hotel = {field: "" for field in FIELDS}
    region, country = COUNTRY_MAP.get(location, ("", ""))

    hotel["Hotel Name"] = name
    hotel["Location"] = location
    hotel["County or Region"] = region
    hotel["Country"] = country

    # Build a simple description from whatever tags exist
    stars = tags.get("stars", "")
    hotel["Hotel Description"] = f"A hotel located in {location}" + (f", rated {stars} stars." if stars else ".")
    hotel["Hotel Category"] = f"{stars}-star" if stars else "Unrated"

    # Address as a stand-in for contact info
    addr_parts = [
        tags.get("addr:housenumber", ""),
        tags.get("addr:street", ""),
        tags.get("addr:city", ""),
    ]
    hotel["Contact Information"] = ", ".join(p for p in addr_parts if p) or tags.get("phone", "")

    hotel["Website URL"] = tags.get("website", tags.get("contact:website", ""))
    hotel["Price Range"] = "Check website"
    hotel["Amenities"] = ", ".join(
        k.replace("_", " ") for k in ["internet_access", "swimming_pool", "air_conditioning"]
        if tags.get(k)
    )

    lat = el.get("lat") or el.get("center", {}).get("lat")
    lon = el.get("lon") or el.get("center", {}).get("lon")
    hotel["Source URL"] = f"https://www.openstreetmap.org/{el['type']}/{el['id']}" if lat else ""

    return hotel


def fetch_hotels_for_location(location):
    print(f"--- {location} ---")
    coords = geocode_location(location)
    if not coords:
        print(f"Could not geocode {location}, skipping.")
        return []
    lat, lon = coords

    elements = query_overpass_hotels(lat, lon)
    hotels = []
    for el in elements:
        hotel = element_to_hotel(el, location)
        if hotel:
            hotels.append(hotel)

    print(f"Found {len(hotels)} hotels")
    return hotels


def write_csv(hotels, filename="data/raw_hotels.csv"):
    os.makedirs(os.path.dirname(filename), exist_ok=True)
    with open(filename, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=FIELDS)
        writer.writeheader()
        writer.writerows(hotels)
    print(f"\nSaved {len(hotels)} hotels to {filename}")


def main():
    print("Travel Africa Hotel Data Collector by Cyrus (OpenStreetMap)")
    print("+" * 50)

    all_hotels = []
    for location in LOCATIONS:
        hotels = fetch_hotels_for_location(location)
        all_hotels.extend(hotels)

        # Save a checkpoint after every location so a crash/rate-limit
        # doesn't lose everything collected so far.
        write_csv(all_hotels, filename="data/raw_hotels_checkpoint.csv")

        # Nominatim usage policy: max 1 request/sec. Overpass is shared/free,
        # so we space requests out more to avoid triggering 429s.
        time.sleep(5)

    # Deduplicate by name + location
    seen = set()
    unique_hotels = []
    for h in all_hotels:
        key = (h["Hotel Name"].lower().strip(), h["Location"])
        if key not in seen:
            seen.add(key)
            unique_hotels.append(h)

    print(f"\nBefore dedup: {len(all_hotels)}")
    print(f"After dedup:  {len(unique_hotels)}")

    write_csv(unique_hotels)


if __name__ == "__main__":
    main()