import csv
import requests
import json
import time

# Set your Spotify API credentials
CLIENT_ID = 'your_client_id'  # Replace with your Client ID
CLIENT_SECRET = 'your_client_secret'  # Replace with your Client Secret

# Function to get the Spotify access token
def get_spotify_token():
    auth_url = 'https://accounts.spotify.com/api/token'
    auth_response = requests.post(auth_url, {
        'grant_type': 'client_credentials',
        'client_id': CLIENT_ID,
        'client_secret': CLIENT_SECRET,
    })
    return auth_response.json()['access_token']

# Function to check if a song exists on Spotify
def song_exists_on_spotify(song_title, artist_name, access_token):
    search_url = 'https://api.spotify.com/v1/search'
    headers = {
        'Authorization': f'Bearer {access_token}'
    }
    query = f'track:{song_title} artist:{artist_name}'
    response = requests.get(search_url, headers=headers, params={'q': query, 'type': 'track', 'limit': 1})

    if response.status_code == 200:
        results = response.json()
        return len(results['tracks']['items']) > 0  # Returns True if track is found
    return False

# Function to filter CSV by checking song validity using Spotify
def filter_songs(input_csv_path, output_csv_path):
    print(f"Filtering songs in the CSV file: {input_csv_path}...")
    access_token = get_spotify_token()
    
    filtered_data = []

    with open(input_csv_path, 'r', encoding='utf-8') as infile:
        reader = csv.DictReader(infile)
        
        for row in reader:
            artist = row['Artist']
            track = row['Track']
            if song_exists_on_spotify(track, artist, access_token):
                filtered_data.append(row)

            time.sleep(0.1)  # Sleep for 100ms to adhere to the rate limit (10 requests/sec)

    # Write the filtered data to a new CSV file
    with open(output_csv_path, 'w', newline='', encoding='utf-8') as outfile:
        fieldnames = ['Artist', 'Track', 'Album', 'Timestamp']
        writer = csv.DictWriter(outfile, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(filtered_data)

    print(f"Filtering complete. {len(filtered_data)} entries retained.")
    print(f"Filtered data saved to: {output_csv_path}")

# Example usage:
input_csv_path = 'lastfm_history.csv'  # Path to your original CSV file
output_csv_path = 'validated_lastfm_history.csv'  # Path to save validated CSV file

filter_songs(input_csv_path, output_csv_path)
