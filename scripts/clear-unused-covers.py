#!/usr/bin/env python3
"""
Check for unused cover images.

This script scans the covers directory and compares it with the albums.json file
to identify cover images that are no longer referenced by any album.

Usage:
    python3 clear-unused-covers.py              # List unused covers
    python3 clear-unused-covers.py --delete    # Delete unused covers
"""

import os
import sys
import json
from pathlib import Path
from typing import Set, List


# Configuration
DATA_DIR = Path(__file__).parent.parent / "public/data"
ALBUMS_JSON = DATA_DIR / "albums.json"
COVERS_DIR = DATA_DIR / "covers"


def get_referenced_covers() -> Set[str]:
    """Extract all cover filenames referenced in albums.json."""
    if not ALBUMS_JSON.exists():
        print(f"Error: {ALBUMS_JSON} not found")
        return set()

    try:
        with open(ALBUMS_JSON, 'r', encoding='utf-8') as f:
            data = json.load(f)

        referenced = set()
        for album in data.get('albums', []):
            cover = album.get('cover')
            if cover:
                # Extract filename from path like "covers/7833de94bbb8.png"
                filename = cover.split('/')[-1]
                referenced.add(filename)

        return referenced
    except (json.JSONDecodeError, KeyError) as e:
        print(f"Error reading {ALBUMS_JSON}: {e}")
        return set()


def get_existing_covers() -> Set[str]:
    """Get all cover files in the covers directory."""
    if not COVERS_DIR.exists():
        print(f"Error: {COVERS_DIR} not found")
        return set()

    # Get all image files in the covers directory
    image_extensions = {'.png', '.jpg', '.jpeg', '.gif', '.webp'}
    existing = set()

    for file in COVERS_DIR.iterdir():
        if file.is_file() and file.suffix.lower() in image_extensions:
            existing.add(file.name)

    return existing


def find_unused_covers(referenced: Set[str], existing: Set[str]) -> List[str]:
    """Find cover files that exist but are not referenced."""
    unused = existing - referenced
    return sorted(unused)


def delete_unused_covers(unused: List[str]) -> int:
    """Delete unused cover files. Returns number of deleted files."""
    deleted_count = 0
    for cover in unused:
        cover_path = COVERS_DIR / cover
        try:
            cover_path.unlink()
            deleted_count += 1
            print(f"  Deleted: {cover}")
        except Exception as e:
            print(f"  Error deleting {cover}: {e}")
    return deleted_count


def main():
    """Main execution method."""
    # Check for --delete flag
    delete_mode = '--delete' in sys.argv or '-d' in sys.argv

    print("=" * 60)
    print("Unused Cover Images Checker")
    print("=" * 60)
    print(f"Albums JSON: {ALBUMS_JSON}")
    print(f"Covers directory: {COVERS_DIR}")
    print()

    # Get referenced and existing covers
    referenced = get_referenced_covers()
    existing = get_existing_covers()

    print(f"Referenced covers in JSON: {len(referenced)}")
    print(f"Existing cover files: {len(existing)}")
    print()

    # Find unused covers
    unused = find_unused_covers(referenced, existing)

    if not unused:
        print("✓ No unused cover images found.")
        print("All cover files are referenced in albums.json")
    else:
        print(f"Found {len(unused)} unused cover image(s):")
        print()
        for cover in unused:
            cover_path = COVERS_DIR / cover
            size_kb = cover_path.stat().st_size / 1024
            print(f"  - {cover} ({size_kb:.1f} KB)")

        print()
        total_size = sum((COVERS_DIR / cover).stat().st_size for cover in unused)
        print(f"Total space that could be freed: {total_size / 1024:.1f} KB")
        print()

        if delete_mode:
            print("Deleting unused covers...")
            deleted = delete_unused_covers(unused)
            print()
            print(f"Deleted {deleted} file(s)")
        else:
            print("To delete these files, run:")
            print("  python3 check-unused-covers.py --delete")

    print("=" * 60)


if __name__ == '__main__':
    main()
