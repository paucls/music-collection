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
  loading = true;
  error: string | null = null;

  constructor(private albumService: AlbumService, private cdr: ChangeDetectorRef) {}

  ngOnInit() {
    this.albumService.getAlbums().subscribe({
      next: (data) => {
        console.log('Received data:', data);
        console.log('Albums array:', data.albums);
        console.log('Albums count:', data.albums.length);
        this.albums = data.albums;
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

  trackById(index: number, album: Album): string {
    return album.id;
  }
}
