/**
 * Main JavaScript file for Whisper Transcription Tool
 */

document.addEventListener('DOMContentLoaded', function() {
    // Initialize tooltips, if any
    initTooltips();
    
    // Check for URL parameters
    handleUrlParameters();
    
    // Add event listeners for common elements
    addGlobalEventListeners();
});

/**
 * Initialize tooltips for elements with data-tooltip attribute
 */
function initTooltips() {
    const tooltipElements = document.querySelectorAll('[data-tooltip]');
    tooltipElements.forEach(element => {
        // Simple tooltip implementation could be added here
        // For now, we're using the title attribute
        if (element.dataset.tooltip) {
            element.title = element.dataset.tooltip;
        }
    });
}

/**
 * Handle URL parameters for page-specific functionality
 */
function handleUrlParameters() {
    const urlParams = new URLSearchParams(window.location.search);
    
    // Handle audio parameter for transcription page
    if (window.location.pathname === '/transcribe') {
        const audioParam = urlParams.get('audio');
        if (audioParam) {
            const infoElement = document.createElement('div');
            infoElement.className = 'info-message';
            infoElement.innerHTML = `
                <i class="fas fa-info-circle"></i>
                <p>Audio aus vorheriger Extraktion: ${audioParam}</p>
            `;
            
            const uploadContainer = document.querySelector('.upload-container');
            if (uploadContainer) {
                uploadContainer.prepend(infoElement);
            }
        }
    }
}

/**
 * Add event listeners for elements that appear on multiple pages
 */
function addGlobalEventListeners() {
    // Mobile navigation toggle
    const navToggle = document.querySelector('.nav-toggle');
    if (navToggle) {
        navToggle.addEventListener('click', function() {
            const nav = document.querySelector('nav ul');
            nav.classList.toggle('active');
        });
    }
    
    // File input styling
    const fileInputs = document.querySelectorAll('input[type="file"]');
    fileInputs.forEach(input => {
        input.addEventListener('change', function() {
            const fileName = this.files[0]?.name || 'Keine Datei ausgewählt';
            const fileNameDisplay = this.parentElement.querySelector('.file-name');
            
            if (fileNameDisplay) {
                fileNameDisplay.textContent = fileName;
            } else {
                const span = document.createElement('span');
                span.className = 'file-name';
                span.textContent = fileName;
                this.parentElement.appendChild(span);
            }
        });
    });
}

/**
 * Format file size in human-readable format
 * @param {number} bytes - File size in bytes
 * @returns {string} Formatted file size
 */
function formatFileSize(bytes) {
    if (bytes === 0) return '0 Bytes';
    
    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
}

/**
 * Show a notification message
 * @param {string} message - Message to display
 * @param {string} type - Message type (success, error, info, warning)
 * @param {number} duration - Duration in milliseconds
 */
function showNotification(message, type = 'info', duration = 5000) {
    // Create notification element
    const notification = document.createElement('div');
    notification.className = `notification ${type}`;
    notification.innerHTML = `
        <div class="notification-content">
            <i class="fas fa-${type === 'success' ? 'check-circle' : 
                              type === 'error' ? 'exclamation-circle' : 
                              type === 'warning' ? 'exclamation-triangle' : 
                              'info-circle'}"></i>
            <p>${message}</p>
        </div>
        <button class="notification-close">
            <i class="fas fa-times"></i>
        </button>
    `;
    
    // Add to document
    document.body.appendChild(notification);
    
    // Add close button functionality
    const closeButton = notification.querySelector('.notification-close');
    closeButton.addEventListener('click', function() {
        notification.classList.add('closing');
        setTimeout(() => {
            notification.remove();
        }, 300);
    });
    
    // Auto-remove after duration
    setTimeout(() => {
        if (document.body.contains(notification)) {
            notification.classList.add('closing');
            setTimeout(() => {
                notification.remove();
            }, 300);
        }
    }, duration);
    
    // Show with animation
    setTimeout(() => {
        notification.classList.add('visible');
    }, 10);
}

/**
 * Format timestamp in HH:MM:SS format
 * @param {number} seconds - Time in seconds
 * @returns {string} Formatted time
 */
function formatTimestamp(seconds) {
    const h = Math.floor(seconds / 3600);
    const m = Math.floor((seconds % 3600) / 60);
    const s = Math.floor(seconds % 60);
    
    return [
        h > 0 ? h.toString().padStart(2, '0') : null,
        m.toString().padStart(2, '0'),
        s.toString().padStart(2, '0')
    ].filter(Boolean).join(':');
}
