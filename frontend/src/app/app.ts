import { Component, signal } from '@angular/core';
import { ContentGeneratorComponent } from './components/content-generator/content-generator.component';

@Component({
  selector: 'app-root',
  imports: [ContentGeneratorComponent],
  templateUrl: './app.html',
  styleUrl: './app.css'
})
export class App {
  protected readonly title = signal('frontend');
}
