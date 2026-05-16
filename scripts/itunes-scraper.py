#!/usr/bin/env python3
"""
Music Library Scraper

This script scans your music folders and extracts album information from audio files.
It extracts embedded artwork from MP3/AAC files and updates a local JSON database.

IMPORTANT: This script NEVER modifies your original music library files.
It only reads from them and writes to the local data/ directory.
"""

import os
import sys
import json
import hashlib
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional

try:
    from mutagen.mp3 import MP3
    from mutagen.mp4 import MP4
    from mutagen.id3 import ID3
    from mutagen.flac import FLAC
    from mutagen.oggvorbis import OggVorbis
except ImportError:
    print("Error: mutagen library is required.")
    print("Install it with: pip install mutagen")
    sys.exit(1)


# Configuration
MUSIC_DIR = Path.home() / "Music"  # Default music directory
# You can also specify a custom path:
# MUSIC_DIR = Path("/path/to/your/music")

DATA_DIR = Path(__file__).parent.parent / "public/data"
ALBUMS_JSON = DATA_DIR / "albums.json"
COVERS_DIR = DATA_DIR / "covers"


class iTunesScraper:
    def __init__(self, music_dir: Path = None):
        self.music_dir = music_dir or MUSIC_DIR
        self.data_dir = DATA_DIR
        self.albums_json = ALBUMS_JSON
        self.covers_dir = COVERS_DIR

        # Ensure data directories exist
        self.data_dir.mkdir(exist_ok=True)
        self.covers_dir.mkdir(exist_ok=True)

        # Load existing database
        self.existing_albums = self._load_existing_albums()

    def _load_existing_albums(self) -> Dict:
        """Load existing albums from JSON database."""
        if self.albums_json.exists():
            try:
                with open(self.albums_json, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    # Create a lookup dict by album key (artist + album)
                    return {
                        self._album_key(album): album
                        for album in data.get('albums', [])
                    }
            except (json.JSONDecodeError, KeyError) as e:
                print(f"Warning: Could not load existing database: {e}")
                return {}
        return {}

    def _album_key(self, album: Dict) -> str:
        """Generate a unique key for an album (artist + album name)."""
        artist = album.get('artist', '').lower().strip()
        title = album.get('title', '').lower().strip()
        return f"{artist}|{title}"

    def _generate_album_id(self, artist: str, title: str) -> str:
        """Generate a unique ID for an album."""
        key = f"{artist}|{title}".encode('utf-8')
        return hashlib.md5(key).hexdigest()[:12]

    def _sanitize_filename(self, filename: str) -> str:
        """Sanitize filename for safe file system usage."""
        # Remove or replace problematic characters
        invalid_chars = '<>:"/\\|?*'
        for char in invalid_chars:
            filename = filename.replace(char, '_')
        return filename.strip()

    def _extract_metadata(self, file_path: Path) -> Optional[Dict]:
        """
        Extract metadata from an audio file.
        This is READ-ONLY - it only reads metadata, never modifies the file.
        """
        try:
            if not file_path.exists():
                return None

            suffix = file_path.suffix.lower()

            if suffix == '.mp3':
                audio = MP3(file_path, ID3=ID3)
                tags = audio.tags

                if not tags:
                    return None

                # Try to get metadata
                title = tags.get('TIT2', [None])[0] if 'TIT2' in tags else None
                artist = tags.get('TPE1', [None])[0] if 'TPE1' in tags else None
                album = tags.get('TALB', [None])[0] if 'TALB' in tags else None
                year = tags.get('TDRC', [None])[0] if 'TDRC' in tags else None
                genre = tags.get('TCON', [None])[0] if 'TCON' in tags else None

                # Extract artwork
                artwork = None
                for tag in tags.values():
                    if tag.FrameID == 'APIC':
                        artwork = tag.data
                        break

            elif suffix in ['.m4a', '.mp4', '.aac']:
                audio = MP4(file_path)

                # MP4 tags use different keys
                title = audio.get('\xa9nam', [None])[0]
                artist = audio.get('\xa9ART', [None])[0]
                album = audio.get('\xa9alb', [None])[0]
                year = audio.get('\xa9day', [None])[0]
                genre = audio.get('\xa9gen', [None])[0]

                # Extract artwork
                artwork = audio.get('covr', [None])[0] if 'covr' in audio else None

            elif suffix == '.flac':
                audio = FLAC(file_path)
                title = audio.get('title', [None])[0]
                artist = audio.get('artist', [None])[0]
                album = audio.get('album', [None])[0]
                year = audio.get('date', [None])[0]
                genre = audio.get('genre', [None])[0]
                artwork = audio.get('picture', [None])[0] if 'picture' in audio else None
                if artwork:
                    artwork = artwork.data

            elif suffix in ['.ogg', '.oga']:
                audio = OggVorbis(file_path)
                title = audio.get('title', [None])[0]
                artist = audio.get('artist', [None])[0]
                album = audio.get('album', [None])[0]
                year = audio.get('date', [None])[0]
                genre = audio.get('genre', [None])[0]
                # Ogg artwork handling is more complex, skip for now
                artwork = None
            else:
                return None

            # Convert year to int if possible
            if year:
                try:
                    year = int(str(year)[:4])  # Take first 4 characters (year)
                except (ValueError, TypeError):
                    year = 0
            else:
                year = 0

            return {
                'title': str(title) if title else None,
                'artist': str(artist) if artist else None,
                'album': str(album) if album else None,
                'year': year,
                'genre': str(genre) if genre else '',
                'artwork': artwork
            }

        except Exception as e:
            print(f"Warning: Could not extract metadata from {file_path}: {e}")
            return None

    def _extract_artwork(self, artwork_data: bytes) -> Optional[bytes]:
        """
        Return artwork data (already extracted in metadata extraction).
        This is READ-ONLY - the data was already extracted from the file.
        """
        return artwork_data

    def _save_cover(self, cover_data: bytes, album_id: str) -> Optional[str]:
        """Save cover image to covers directory."""
        try:
            # Determine image type from data
            if cover_data.startswith(b'\xff\xd8\xff'):
                ext = '.jpg'
            elif cover_data.startswith(b'\x89PNG'):
                ext = '.png'
            else:
                ext = '.jpg'  # Default to jpg

            cover_filename = f"{album_id}{ext}"
            cover_path = self.covers_dir / cover_filename

            # Write the cover image (this is in our data dir, not music library)
            with open(cover_path, 'wb') as f:
                f.write(cover_data)

            return f"covers/{cover_filename}"
        except Exception as e:
            print(f"Warning: Could not save cover for {album_id}: {e}")
            return None

    def _parse_library(self) -> List[Dict]:
        """Scan music directory and extract album information from audio files."""
        if not self.music_dir.exists():
            print(f"Error: Music directory not found at {self.music_dir}")
            print("Please update the MUSIC_DIR in the script.")
            sys.exit(1)

        print(f"Scanning music directory: {self.music_dir}")
        print("This may take a moment if you have a large library...")

        # Supported audio file extensions
        audio_extensions = {'.mp3', '.m4a', '.mp4', '.aac', '.flac', '.ogg', '.oga', '.wma', '.wav'}

        albums_data = {}
        processed_count = 0
        file_count = 0

        # Recursively scan the music directory
        for root, dirs, files in os.walk(self.music_dir):
            for file in files:
                file_path = Path(root) / file

                if file_path.suffix.lower() not in audio_extensions:
                    continue

                file_count += 1
                if file_count % 100 == 0:
                    print(f"Scanned {file_count} files...")

                # Extract metadata from the audio file
                metadata = self._extract_metadata(file_path)

                if not metadata or not metadata.get('album') or not metadata.get('artist'):
                    continue

                album_name = metadata['album']
                artist = metadata['artist']
                album_key = f"{artist.lower().strip()}|{album_name.lower().strip()}"

                # Skip if we already have this album
                if album_key in albums_data:
                    continue

                # Extract artwork
                artwork = metadata.get('artwork')
                cover_path = None

                if artwork:
                    cover_path = self._save_cover(artwork, self._generate_album_id(artist, album_name))

                albums_data[album_key] = {
                    'id': self._generate_album_id(artist, album_name),
                    'title': album_name,
                    'artist': artist,
                    'year': metadata.get('year', 0),
                    'genre': metadata.get('genre', ''),
                    'type': 'digital',  # Can be overridden manually for CDs
                    'cover': cover_path,
                    'dateAdded': datetime.now().isoformat()
                }

                processed_count += 1
                if processed_count % 10 == 0:
                    print(f"Processed {processed_count} albums...")

        print(f"Scanned {file_count} audio files")
        print(f"Found {len(albums_data)} unique albums")
        return list(albums_data.values())

    def run(self):
        """Main execution method."""
        print("=" * 60)
        print("Music Library Scraper")
        print("=" * 60)
        print(f"Music directory: {self.music_dir}")
        print(f"Data directory: {self.data_dir}")
        print()

        # Parse Music library
        new_albums = self._parse_library()

        # Compare with existing database
        added_albums = []
        updated_albums = []

        for album in new_albums:
            key = self._album_key(album)
            if key in self.existing_albums:
                # Album exists, check if it needs updating
                existing = self.existing_albums[key]
                # Only update if cover is missing but we now have one
                if not existing.get('cover') and album.get('cover'):
                    album['dateAdded'] = existing['dateAdded']  # Preserve original date
                    updated_albums.append(album)
            else:
                added_albums.append(album)

        # Merge all albums
        all_albums = list(self.existing_albums.values())

        # Remove updated albums from existing
        for updated in updated_albums:
            key = self._album_key(updated)
            all_albums = [a for a in all_albums if self._album_key(a) != key]

        # Add updated and new albums
        all_albums.extend(updated_albums)
        all_albums.extend(added_albums)

        # Sort by date added (newest first)
        all_albums.sort(key=lambda x: x.get('dateAdded', ''), reverse=True)

        # Write to JSON
        output_data = {
            'albums': all_albums,
            'lastUpdated': datetime.now().isoformat()
        }

        with open(self.albums_json, 'w', encoding='utf-8') as f:
            json.dump(output_data, f, indent=2, ensure_ascii=False)

        print()
        print("=" * 60)
        print("Summary:")
        print(f"  Total albums in database: {len(all_albums)}")
        print(f"  New albums added: {len(added_albums)}")
        print(f"  Albums updated: {len(updated_albums)}")
        print()
        print(f"Database written to: {self.albums_json}")
        print("=" * 60)

        if added_albums:
            print("\nNew albums added:")
            for album in added_albums[:10]:  # Show first 10
                print(f"  - {album['artist']} - {album['title']}")
            if len(added_albums) > 10:
                print(f"  ... and {len(added_albums) - 10} more")


def main():
    """Main entry point."""
    # Allow custom music directory via command line
    music_dir = None
    if len(sys.argv) > 1:
        music_dir = Path(sys.argv[1])

    scraper = iTunesScraper(music_dir)
    scraper.run()


if __name__ == '__main__':
    main()
