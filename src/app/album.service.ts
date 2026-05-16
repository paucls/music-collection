import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable } from 'rxjs';

export interface Album {
  id: string;
  title: string;
  artist: string;
  year: number;
  type: 'cd' | 'digital';
  cover: string;
  dateAdded: string;
  genre?: string;
}

export interface MusicCollection {
  albums: Album[];
  lastUpdated: string | null;
}

@Injectable({
  providedIn: 'root'
})
export class AlbumService {
  constructor(private http: HttpClient) {}

  getAlbums(): Observable<MusicCollection> {
    return this.http.get<MusicCollection>('/data/albums.json');
  }
}
