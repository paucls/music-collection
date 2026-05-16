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
  selectedArtist: string = '';
  artists: string[] = [];

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
    this.selectedArtist = artist;
    if (artist === '') {
      this.filteredAlbums = [...this.albums];
    } else {
      this.filteredAlbums = this.albums.filter(album => album.artist === artist);
    }
  }

  trackById(index: number, album: Album): string {
    return album.id;
  }
}
