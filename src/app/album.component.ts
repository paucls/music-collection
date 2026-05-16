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
}
