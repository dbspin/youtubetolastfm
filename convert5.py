import re
import csv
from datetime import datetime
import time

# Regular expression to find video titles and timestamps
TITLE_REGEX = re.compile(r'<a href="[^"]+">(.*?)<\/a>', re.IGNORECASE)
TIMESTAMP_REGEX = re.compile(r'(\d{1,2} \w{3} \d{4}, \d{1,2}:\d{2}:\d{2} \w{3})', re.IGNORECASE)

# Function to parse the YouTube watch history HTML file incrementally
def parse_watch_history(file_path):
    print("Parsing the watch-history.html file...")

    start_time = time.time()
    watch_data = []

    with open(file_path, 'r', encoding='utf-8') as file:
        content = file.read()

    # Find all video titles
    titles = TITLE_REGEX.findall(content)
    timestamps = TIMESTAMP_REGEX.findall(content)

    total_entries = min(len(titles), len(timestamps))  # Make sure we don't go out of bounds
    print(f"Found {total_entries} entries to process...")

    for i in range(total_entries):
        title = titles[i].strip()
        timestamp_str = timestamps[i].strip()

        # Convert timestamp to ISO 8601 format
        try:
            timestamp = datetime.strptime(timestamp_str, '%d %b %Y, %H:%M:%S %Z')
            timestamp_iso = timestamp.isoformat()
        except ValueError:
            continue  # Skip entries with malformed timestamps
        
        watch_data.append((title, timestamp_iso))

        # Print progress every 100 entries
        if (i + 1) % 100 == 0 or (i + 1) == total_entries:
            percent_done = ((i + 1) / total_entries) * 100
            print(f"Parsing progress: {i + 1}/{total_entries} ({percent_done:.2f}%)")

    end_time = time.time()
    print(f"Finished parsing in {end_time - start_time:.2f} seconds.")
    return watch_data

# Function to extract artist and track from video titles
def extract_artist_track(title):
    # A very basic regex-based approach to split the title into artist and track.
    separators = [' - ', ' | ']
    for sep in separators:
        if sep in title:
            artist, track = title.split(sep, 1)
            return artist.strip(), track.strip()
    
    # If no separator is found, return the title as both artist and track (fallback)
    return title, title

# Function to write parsed data to CSV in Last.fm format with progress indicator
def write_to_csv(watch_data, output_csv_path):
    total_entries = len(watch_data)
    print(f"Writing {total_entries} entries to CSV...")

    with open(output_csv_path, 'w', newline='', encoding='utf-8') as csvfile:
        fieldnames = ['Artist', 'Track', 'Album', 'Timestamp']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()

        # Processing each entry with progress
        for i, (title, timestamp) in enumerate(watch_data):
            artist, track = extract_artist_track(title)
            writer.writerow({'Artist': artist, 'Track': track, 'Album': '', 'Timestamp': timestamp})
            
            # Print progress every 100 entries
            if (i + 1) % 100 == 0 or (i + 1) == total_entries:
                percent_done = ((i + 1) / total_entries) * 100
                print(f"CSV writing progress: {i + 1}/{total_entries} ({percent_done:.2f}%)")
    
    print("CSV writing complete.")

# Main function to run the conversion with progress and real-time updates
def convert_youtube_history_to_lastfm_csv(html_file_path, output_csv_path):
    # Parsing stage with progress updates
    watch_data = parse_watch_history(html_file_path)

    # Writing to CSV with progress updates
    write_to_csv(watch_data, output_csv_path)
    print(f"Successfully converted and saved to {output_csv_path}")

# Example usage:
html_file_path = 'watch-history.html'  # Path to your watch-history.html file
output_csv_path = 'lastfm_history.csv'  # Output CSV file

convert_youtube_history_to_lastfm_csv(html_file_path, output_csv_path)
