import { Component, ChangeDetectorRef } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { ApiService } from '../../services/api.service';
import { Observable } from 'rxjs';
import { finalize } from 'rxjs/operators';

@Component({
    selector: 'app-content-generator',
    standalone: true,
    imports: [CommonModule, FormsModule],
    templateUrl: './content-generator.component.html',
    styleUrls: ['./content-generator.component.css']
})
export class ContentGeneratorComponent {
    title: string = '';
    body: string = '';
    platforms: string[] = ['facebook', 'instagram', 'whatsapp', 'linkedin', 'tiktok'];
    selectedPlatforms: { [key: string]: boolean } = {
        facebook: true,
        instagram: true,
        whatsapp: true,
        linkedin: true,
        tiktok: true
    };

    isLoading: boolean = false;
    results: any = null;
    error: string = '';
    sidebarOpen: boolean = false;

    constructor(
        private apiService: ApiService,
        private cdr: ChangeDetectorRef
    ) { }

    // Chat history structure
    chatHistory: any[] = [];

    // Track publishing states: { messageIndex: { platform: 'publishing' | 'published' } }
    publishingStates: { [key: string]: { [platform: string]: string } } = {};

    newChat() {
        if (this.chatHistory.length > 0 && confirm('¿Iniciar una nueva conversación? Se perderá el historial actual.')) {
            this.chatHistory = [];
            this.title = '';
            this.body = '';
            this.error = '';
        }
    }

    toggleSidebar() {
        this.sidebarOpen = !this.sidebarOpen;
    }

    generate() {
        const selected = Object.keys(this.selectedPlatforms).filter(p => this.selectedPlatforms[p]);

        if (selected.length === 0) {
            alert('Por favor selecciona al menos una plataforma.');
            return;
        }

        this.isLoading = true;
        this.error = '';

        // Add user message to history
        this.chatHistory.push({
            type: 'user',
            title: this.title,
            body: this.body,
            timestamp: new Date()
        });

        const payload = {
            title: this.title,
            body: this.body,
            platforms: selected
        };

        // Clear inputs
        const currentTitle = this.title;
        const currentBody = this.body;
        this.title = '';
        this.body = '';

        this.apiService.generateContent(payload)
            .pipe(finalize(() => {
                console.log('Finalize called - setting isLoading to false'); // DEBUG
                this.isLoading = false;
                this.cdr.detectChanges(); // Force update
            }))
            .subscribe({
                next: (data) => {
                    console.log('Backend response:', data); // DEBUG
                    // Add AI response to history
                    this.chatHistory.push({
                        type: 'ai',
                        content: data,
                        timestamp: new Date()
                    });
                    this.cdr.detectChanges(); // Force update again just in case
                },
                error: (err) => {
                    console.error('API Error:', err); // DEBUG
                    this.error = 'Ocurrió un error al generar el contenido. Inténtalo de nuevo.';
                    // Restore inputs on error
                    this.title = currentTitle;
                    this.body = currentBody;
                    this.cdr.detectChanges(); // Force update
                }
            });
    }

    publish(platform: string, content: any, messageIndex: number) {
        // Create unique key for this message
        const msgKey = `msg_${messageIndex}`;

        // Check if already publishing or published
        if (this.publishingStates[msgKey]?.[platform]) {
            return; // Already publishing or published
        }

        if (!confirm(`¿Estás seguro de publicar en ${platform}?`)) return;

        // Initialize state object if needed
        if (!this.publishingStates[msgKey]) {
            this.publishingStates[msgKey] = {};
        }

        // Set to publishing state
        this.publishingStates[msgKey][platform] = 'publishing';
        this.cdr.detectChanges();

        const text = content.text || content.caption || content.message || content.script || '';
        const mediaUrl = content.media_url;
        const videoUrl = content.video_url || content.display_video_url;

        const payload = {
            platform: platform,
            text: text,
            media_url: mediaUrl,
            video_url: videoUrl
        };

        this.apiService.publishContent(payload).subscribe({
            next: (res: any) => {
                if (res.error) {
                    alert(`Error: ${res.message}`);
                    // Reset state on error
                    delete this.publishingStates[msgKey][platform];
                } else {
                    // Set to published state
                    this.publishingStates[msgKey][platform] = 'published';
                    this.cdr.detectChanges();
                }
            },
            error: (err) => {
                console.error(err);
                alert('Error al publicar en el servidor.');
                // Reset state on error
                delete this.publishingStates[msgKey][platform];
                this.cdr.detectChanges();
            }
        });
    }

    getPublishButtonState(messageIndex: number, platform: string): string {
        const msgKey = `msg_${messageIndex}`;
        return this.publishingStates[msgKey]?.[platform] || '';
    }

    isPublishDisabled(messageIndex: number, platform: string): boolean {
        if (platform === 'tiktok') return true;
        const state = this.getPublishButtonState(messageIndex, platform);
        return state === 'publishing' || state === 'published';
    }

    getObjectKeys(obj: any): string[] {
        if (!obj) return [];
        return Object.keys(obj);
    }

    getMediaUrl(content: any): string | null {
        const url = content.display_url || content.media_url || null;
        if (!url) console.warn('No media URL for content:', content);
        return url;
    }

    getVideoUrl(content: any): string | null {
        return content.display_video_url || content.video_url || null;
    }

    getTextContent(content: any): string {
        return content.text || content.caption || content.message || content.script || '';
    }

    handleImageError(event: any, platform: string) {
        console.error(`Error loading image for ${platform}:`, event);
        event.target.src = 'assets/placeholder.png'; // Fallback or just keep broken
    }
}
