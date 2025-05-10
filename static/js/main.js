/**
 * File Mapper - Main JavaScript
 * Contains general utility functions used throughout the application
 */

// Initialize tooltips
document.addEventListener('DOMContentLoaded', function() {
    // Initialize all Bootstrap tooltips
    const tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    tooltipTriggerList.map(function(tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl);
    });
    
    // Initialize all Bootstrap popovers
    const popoverTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="popover"]'));
    popoverTriggerList.map(function(popoverTriggerEl) {
        return new bootstrap.Popover(popoverTriggerEl);
    });
    
    // Auto-dismiss alerts after 5 seconds
    setTimeout(function() {
        const alertList = document.querySelectorAll('.alert-dismissible');
        alertList.forEach(function(alert) {
            const bsAlert = new bootstrap.Alert(alert);
            bsAlert.close();
        });
    }, 5000);
});

/**
 * Format a date string into a more readable format
 * @param {string} dateString - ISO date string
 * @return {string} Formatted date string
 */
function formatDate(dateString) {
    if (!dateString) return '';
    
    const date = new Date(dateString);
    if (isNaN(date)) return dateString;
    
    return date.toLocaleString();
}

/**
 * Format a file size in bytes to a human-readable format
 * @param {number} bytes - Size in bytes
 * @return {string} Formatted size (e.g., "1.5 KB", "3.2 MB")
 */
function formatFileSize(bytes) {
    if (bytes === 0) return '0 Bytes';
    
    const sizes = ['Bytes', 'KB', 'MB', 'GB', 'TB'];
    const i = Math.floor(Math.log(bytes) / Math.log(1024));
    
    return parseFloat((bytes / Math.pow(1024, i)).toFixed(1)) + ' ' + sizes[i];
}

/**
 * Toggle password visibility in password fields
 * @param {string} fieldId - ID of the password field
 * @param {string} toggleId - ID of the toggle button/icon
 */
function togglePasswordVisibility(fieldId, toggleId) {
    const passwordField = document.getElementById(fieldId);
    const toggleButton = document.getElementById(toggleId);
    
    if (passwordField.type === 'password') {
        passwordField.type = 'text';
        toggleButton.innerHTML = '<i class="fas fa-eye-slash"></i>';
    } else {
        passwordField.type = 'password';
        toggleButton.innerHTML = '<i class="fas fa-eye"></i>';
    }
}
