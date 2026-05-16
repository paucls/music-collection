# Music Collection

A simple, static Angular application to display your music collection (CDs and digital albums). The app reads all data from local files without requiring an API or backend server.

## Overview

This project consists of three main components:

1. **Angular Web Application** - A static frontend that displays your music collection
2. **iTunes Scraper Script** - A local script that reads your iTunes library, detects new music, extracts album metadata and covers, and updates the data files
3. **Data Files** - JSON files containing your music collection data

## Architecture

```
music-collection/
├── src/                          # Angular application
│   ├── app/
│   │   ├── components/           # Angular components
│   │   ├── services/             # Data loading services
│   │   └── assets/               # Static assets (album covers)
│   └── ...
├── data/                         # Music collection data
│   ├── albums.json               # Main album database
│   └── covers/                   # Album cover images
├── scripts/                      # Utility scripts
│   └── itunes-scraper.py         # iTunes library scraper
├── .github/
│   └── workflows/
│       └── deploy.yml            # GitHub Actions workflow
└── README.md
```

## How It Works

### Data Flow

1. **iTunes Scraper Script** runs locally on your MacBook Pro
   - Reads your iTunes Music Library.xml file
   - Detects new albums not yet in the database
   - Extracts album metadata (name, artist, year, etc.)
   - Extracts or downloads album cover artwork
   - Updates `data/albums.json` with new entries
   - Saves cover images to `data/covers/`

2. **Git Push** - After running the scraper, you commit and push changes to GitHub

3. **GitHub Actions** automatically:
   - Builds the Angular application
   - Deploys to GitHub Pages
   - Your updated collection is live on the web

4. **Angular App** reads the data files directly:
   - Loads `data/albums.json` at build time or runtime
   - Displays albums in a grid/list view
   - Shows cover images from `data/covers/`

### Data Structure

The `albums.json` file will contain:

```json
{
  "albums": [
    {
      "id": "unique-id",
      "title": "Album Title",
      "artist": "Artist Name",
      "year": 2024,
      "type": "cd" | "digital",
      "cover": "covers/album-cover.jpg",
      "dateAdded": "2024-05-16",
      "genre": "Rock"
    }
  ],
  "lastUpdated": "2024-05-16T20:00:00Z"
}
```

## Components

### 1. Angular Web Application

- **Framework**: Angular (latest stable version)
- **Styling**: CSS/SCSS (can be extended with Tailwind if needed)
- **Features**:
  - Display albums in a responsive grid
  - Filter by artist, genre, or type (CD/digital)
  - Search functionality
  - Album detail view
  - Sort options (by date added, year, artist)

### 2. Music Library Scraper Script

- **Language**: Python 3
- **Input**: Music folder (scans audio files directly)
- **Features**:
  - Scan music folder recursively for audio files (read-only)
  - Extract metadata from MP3, AAC, FLAC, OGG, etc. using mutagen
  - Identify albums by album name + artist from file metadata
  - Compare with existing database to find new additions
  - Extract album artwork embedded in audio files (not downloaded)
  - Generate unique IDs for each album
  - Update JSON database
  - Handle edge cases (missing artwork, various artists albums)

### 3. GitHub Actions CI/CD

- **Triggers**: Push to main branch
- **Steps**:
  1. Checkout code
  2. Setup Node.js
  3. Install dependencies
  4. Build Angular app (including data files in assets)
  5. Deploy to GitHub Pages

## Setup Instructions

### Prerequisites

- Node.js (v18 or higher)
- Angular CLI
- Python 3 (for the scraper script)
- Git
- GitHub account

### Initial Setup

1. **Clone the repository**
   ```bash
   git clone https://github.com/your-username/music-collection.git
   cd music-collection
   ```

2. **Install Angular dependencies**
   ```bash
   npm install
   ```

3. **Set up data directory**
   ```bash
   mkdir -p data/covers
   ```

4. **Initialize albums.json**
   ```bash
   echo '{"albums": [], "lastUpdated": null}' > data/albums.json
   ```

5. **Run the Music library scraper**
   ```bash
   python3 scripts/itunes-scraper.py
   ```
   
   By default, it scans `~/Music`. To specify a custom directory:
   ```bash
   python3 scripts/itunes-scraper.py /path/to/your/music
   ```

6. **Commit and push**
   ```bash
   git add .
   git commit -m "Initial music collection"
   git push origin main
   ```

7. **Enable GitHub Pages**
   - Go to repository Settings > Pages
   - Select GitHub Actions as source

## Usage

### Adding New Music

1. Add new albums to your iTunes library
2. Run the scraper script:
   ```bash
   python3 scripts/itunes-scraper.py
   ```
3. Review the changes in `data/albums.json`
4. Commit and push:
   ```bash
   git add data/
   git commit -m "Add new albums"
   git push origin main
   ```
5. GitHub Actions will automatically deploy the updated site

### Local Development

Run the Angular development server:
```bash
ng serve
```

The app will be available at `http://localhost:4200`

## Deployment

The app is automatically deployed to GitHub Pages via GitHub Actions when you push to the main branch. Your site will be available at:

```
https://your-username.github.io/music-collection/
```

## Future Enhancements

- Support for manual entry of albums not in iTunes
- Import/export functionality
- Statistics dashboard (total albums, by genre, by year)
- Dark mode
- Mobile app version
- Integration with music streaming services for playback

## License

MIT License - feel free to use this project for your own music collection.

## Contributing

This is a personal project, but suggestions and improvements are welcome!
