# Music Collection

A web application for browsing and filtering your music library. Displays albums with cover art, organized by artist and format (vinyl, CD, digital MP3, digital ALAC).

## Features

- **Album Browser**: View your entire music collection with album artwork
- **Filtering**: Filter albums by artist and format type
- **Metadata Extraction**: Automatically extracts album information from your music files

## Music Library Scraper

The included Python script (`scripts/itunes-scraper.py`) scans your music directory and extracts album metadata from audio files:

- **Supported formats**: MP3, M4A, AAC, FLAC, OGG, WAV
- **Extracts**: Artist, album title, year, genre, and embedded artwork
- **Safe**: Read-only operation - never modifies your original music files
- **Database**: Stores results in `public/data/albums.json` with cover images in `public/data/covers/`

### Running the Scraper

```bash
# Install dependencies
pip install -r scripts/requirements.txt

# Run with default music directory (~/Music)
python scripts/itunes-scraper.py

# Or specify a custom directory
python scripts/itunes-scraper.py /Users/YOUR_USERNAME/Music/Music/Media.localized/Music
```

## Running the App

```bash
# Install dependencies
npm install

# Start development server
ng serve

# Build for production
ng build
```

The app will be available at `http://localhost:4200`
