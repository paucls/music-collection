import { Component, Input } from '@angular/core';
import { CommonModule } from '@angular/common';
import { Album } from './album.service';

@Component({
  selector: 'app-album',
  standalone: true,
  imports: [CommonModule],
  templateUrl: './album.component.html',
  styleUrls: ['./album.component.css']
})
export class AlbumComponent {
  @Input() album!: Album;

  formatType(type: string): string {
    if (type === 'digital-mp3') {
      return 'digital MP3';
    } else if (type === 'digital-alac') {
      return 'digital ALAC';
    }
    return type;
  }
}
