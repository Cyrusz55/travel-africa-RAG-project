import pandas as pd
df = pd.read_csv("data/raw_data/raw_hotels.csv")

df = df.dropna(subset = "Hotel Name")

df = df.drop_duplicates(subset = ["Hotel Name", "Location"])

location_map = {"Mombasa City": "Mombasa", "Diani Beach": "Diani"}

df["Location"] = df["Location"].replace(location_map)

df["Hotel Description"] = df["Hotel Description"].fillna("No description avilable")


# replace nan amenities with "No amenities listed"
df["Amenities"] = df["Amenities"].fillna("No amenities listed")

# replace nan contact information with "No contact information available"
df["Contact Information"] = df["Contact Information"].fillna("No contact information available")

# replace nan website url with "No website available"
df["Website URL"] = df["Website URL"].fillna("No website available")



# dropping all the empty columns
df = df.drop(columns=["Room Types", "Rating", "Review Summary", "Nearby Attractions", "Image URL"])


df.to_csv("data/clean_data/cleaned_hotels.csv", index=False)
print(f"Cleaned dataset: {len(df)} hotels")