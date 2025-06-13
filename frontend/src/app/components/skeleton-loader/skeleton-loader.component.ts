/**
 * Skeleton loader component for displaying loading states.
 * 
 * This component provides a placeholder UI that mimics the structure of the story cards
 * while content is loading. It uses Tailwind CSS for styling and includes:
 * - Title placeholder
 * - Meta information placeholders
 * - Content text placeholders
 * - Action button placeholders
 * 
 * The component uses CSS animations to create a pulsing effect that indicates loading state.
 */
import { Component } from '@angular/core';
import { CommonModule } from '@angular/common';

@Component({
  selector: 'app-skeleton-loader',
  standalone: true,
  imports: [CommonModule],
  template: `
    <div class="container max-w-[1400px] mx-auto px-4 sm:px-6 lg:px-8 py-8">
      <!-- Grid layout for skeleton cards -->
      <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        <!-- Generate 6 skeleton cards -->
        <div *ngFor="let i of [1,2,3,4,5,6]" 
             class="bg-white rounded-xl shadow-sm border border-gray-100 p-6 animate-pulse">
          <!-- Title placeholder with 75% width -->
          <div class="h-6 bg-gray-200 rounded w-3/4 mb-4"></div>
          
          <!-- Meta information placeholders (points, author, etc.) -->
          <div class="flex items-center space-x-4 mb-6">
            <div class="h-4 bg-gray-200 rounded w-1/4"></div>
            <div class="h-4 bg-gray-200 rounded w-1/4"></div>
          </div>
          
          <!-- Content text placeholders with varying widths -->
          <div class="space-y-3">
            <div class="h-4 bg-gray-200 rounded w-full"></div>
            <div class="h-4 bg-gray-200 rounded w-5/6"></div>
            <div class="h-4 bg-gray-200 rounded w-4/6"></div>
          </div>
          
          <!-- Action button placeholders -->
          <div class="mt-6 flex space-x-4">
            <div class="h-8 bg-gray-200 rounded w-1/3"></div>
            <div class="h-8 bg-gray-200 rounded w-1/3"></div>
          </div>
        </div>
      </div>
    </div>
  `,
  styles: [`
    :host {
      display: block;
    }
    
    /* Pulsing animation for loading effect */
    .animate-pulse {
      animation: pulse 2s cubic-bezier(0.4, 0, 0.6, 1) infinite;
    }
    
    @keyframes pulse {
      0%, 100% {
        opacity: 1;
      }
      50% {
        opacity: .5;
      }
    }
  `]
})
export class SkeletonLoaderComponent {} 