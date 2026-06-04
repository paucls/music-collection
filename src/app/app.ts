import { Component, OnInit, ChangeDetectorRef } from '@angular/core';
import { CommonModule } from '@angular/common';
import { AlbumService, Album } from './album.service';
import { AlbumComponent } from './album.component';

@Component({
  selector: 'app-root',
  standalone: true,
  imports: [CommonModule, AlbumComponent],
  templateUrl: './app.html',
  styleUrl: './app.css'
})
export class App implements OnInit {
  albums: Album[] = [];
  filteredAlbums: Album[] = [];
  loading = true;
  error: string | null = null;
  selectedArtists: Set<string> = new Set();
  artists: string[] = [];
  showDropdown = false;
  selectedTypes: Set<string> = new Set();
  types: string[] = ['vinyl', 'CD', 'digital-mp3', 'digital-alac'];
  showTypeDropdown = false;

  constructor(private albumService: AlbumService, private cdr: ChangeDetectorRef) {}

  ngOnInit() {
    this.albumService.getAlbums().subscribe({
      next: (data) => {
        console.log('Received data:', data);
        console.log('Albums array:', data.albums);
        console.log('Albums count:', data.albums.length);
        this.albums = data.albums;
        this.sortAlbums();
        this.extractArtists();
        this.filteredAlbums = [...this.albums];
        console.log('After assignment - this.albums:', this.albums);
        console.log('After assignment - this.albums.length:', this.albums.length);
        this.loading = false;
        this.cdr.detectChanges();
      },
      error: (err) => {
        this.error = 'Failed to load albums';
        this.loading = false;
        console.error(err);
      }
    });
  }

  sortAlbums() {
    this.albums.sort((a, b) => {
      const artistCompare = a.artist.localeCompare(b.artist);
      if (artistCompare !== 0) return artistCompare;
      return a.title.localeCompare(b.title);
    });
  }

  extractArtists() {
    const uniqueArtists = new Set(this.albums.map(album => album.artist));
    this.artists = Array.from(uniqueArtists).sort();
  }

  filterByArtist(artist: string) {
    if (this.selectedArtists.has(artist)) {
      this.selectedArtists.delete(artist);
    } else {
      this.selectedArtists.add(artist);
    }
    this.applyFilter();
  }

  applyFilter() {
    let result = [...this.albums];

    if (this.selectedArtists.size > 0) {
      result = result.filter(album => this.selectedArtists.has(album.artist));
    }

    if (this.selectedTypes.size > 0) {
      result = result.filter(album => this.selectedTypes.has(album.type));
    }

    this.filteredAlbums = result;
  }

  filterByType(type: string) {
    if (this.selectedTypes.has(type)) {
      this.selectedTypes.delete(type);
    } else {
      this.selectedTypes.add(type);
    }
    this.applyFilter();
  }

  toggleTypeDropdown() {
    this.showTypeDropdown = !this.showTypeDropdown;
  }

  getSelectedTypeCount(): number {
    return this.selectedTypes.size;
  }

  toggleDropdown() {
    this.showDropdown = !this.showDropdown;
  }

  getSelectedCount(): number {
    return this.selectedArtists.size;
  }

  trackById(index: number, album: Album): string {
    return album.id;
  }

  formatType(type: string): string {
    if (type === 'digital-mp3') {
      return 'digital MP3';
    } else if (type === 'digital-alac') {
      return 'digital ALAC';
    }
    return type;
  }

  getAlbumCount(albums: Album[]): number {
    const albumKeys = new Set<string>();

    albums.forEach(album => {
      // Remove disc information from title to get base album name
      // Matches patterns like "[Disc 1]", "[Disc 2]", "[Disc 1 of 2]", etc.
      const baseTitle = album.title.replace(/\s*\[Disc\s+\d+(?:\s+of\s+\d+)?\]\s*/gi, '').trim();
      // Create a unique key combining artist and base album title
      const key = `${album.artist}|${baseTitle}`;
      albumKeys.add(key);
    });

    return albumKeys.size;
  }
}
