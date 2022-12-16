import { Injectable } from '@angular/core';
import { shuffle, first, chunk } from 'lodash';
import * as objectHash from 'object-hash';
import { pallette } from '../../entity/palette';

@Injectable({
  providedIn: 'root',
})
export class ColorService {
  constructor() {}

  private hash(text: string): number {
    return parseInt(objectHash.MD5(text), 16);
  }

  rgb(hexColor: string): number[] {
    const parts = chunk(hexColor.replace('#', '').split(''), 2).map((p) =>
      p.join('')
    );
    return parts.map((h) => parseInt(h, 16));
  }

  rgba(color: string, opacity: number): string {
    return `rgba(${this.rgb(color).join(',')},${opacity})`;
  }

  // export(item: ExportEntity, shades=['800']): string {
  //   const text = item.name;
  //   return this.color(text, shades);
  // }

  color(text: string, shades: string[] = ['500']): string {
    const hash = this.hash(text);
    const shade = first(shuffle(shades)) || '500';
    const size = pallette['500'].length;
    const idx = hash % size;
    return pallette[shade][idx];
  }
}
