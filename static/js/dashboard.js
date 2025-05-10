/**
 * Dashboard charts and functionality
 */

/**
 * Create a chart showing distribution of file types
 * @param {Array} uploads - Array of upload objects with filename property
 */
function createFileTypeChart(uploads) {
    if (!uploads || uploads.length === 0) return;
    
    const typeCount = {};
    
    // Count file types
    uploads.forEach(upload => {
        const extension = upload.filename.split('.').pop().toUpperCase();
        typeCount[extension] = (typeCount[extension] || 0) + 1;
    });
    
    // Prepare chart data
    const labels = Object.keys(typeCount);
    const data = Object.values(typeCount);
    
    // Create pie chart
    const ctx = document.getElementById('fileTypeChart').getContext('2d');
    new Chart(ctx, {
        type: 'doughnut',
        data: {
            labels: labels,
            datasets: [{
                data: data,
                backgroundColor: [
                    'rgba(255, 99, 132, 0.7)',
                    'rgba(54, 162, 235, 0.7)',
                    'rgba(255, 206, 86, 0.7)',
                    'rgba(75, 192, 192, 0.7)',
                    'rgba(153, 102, 255, 0.7)'
                ],
                borderColor: 'rgba(255, 255, 255, 0.7)',
                borderWidth: 1
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                title: {
                    display: true,
                    text: 'File Types Distribution',
                    color: '#fff'
                },
                legend: {
                    position: 'right',
                    labels: {
                        color: '#fff'
                    }
                }
            }
        }
    });
}

/**
 * Create a chart showing uploads over time
 * @param {Array} uploads - Array of upload objects with uploaded_at property
 */
function createUploadTimelineChart(uploads) {
    if (!uploads || uploads.length === 0) return;
    
    // Get dates for the last 30 days
    const dates = [];
    const counts = [];
    const today = new Date();
    
    // Initialize all dates with 0 counts
    for (let i = 29; i >= 0; i--) {
        const date = new Date(today);
        date.setDate(today.getDate() - i);
        const dateStr = date.toISOString().split('T')[0];
        dates.push(dateStr);
        counts.push(0);
    }
    
    // Count uploads per day
    uploads.forEach(upload => {
        const uploadDate = upload.uploaded_at.split('T')[0];
        const index = dates.indexOf(uploadDate);
        if (index !== -1) {
            counts[index]++;
        }
    });
    
    // Format labels for display (just show day and month for readability)
    const formattedDates = dates.map(dateStr => {
        const date = new Date(dateStr);
        return `${date.getDate()}/${date.getMonth() + 1}`;
    });
    
    // Create line chart
    const ctx = document.getElementById('uploadTimelineChart').getContext('2d');
    new Chart(ctx, {
        type: 'line',
        data: {
            labels: formattedDates,
            datasets: [{
                label: 'Uploads',
                data: counts,
                backgroundColor: 'rgba(54, 162, 235, 0.2)',
                borderColor: 'rgba(54, 162, 235, 1)',
                borderWidth: 2,
                tension: 0.3,
                fill: true
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                title: {
                    display: true,
                    text: 'Upload Activity (Last 30 Days)',
                    color: '#fff'
                },
                legend: {
                    display: false
                }
            },
            scales: {
                y: {
                    beginAtZero: true,
                    ticks: {
                        stepSize: 1,
                        color: '#fff'
                    },
                    grid: {
                        color: 'rgba(255, 255, 255, 0.1)'
                    }
                },
                x: {
                    ticks: {
                        maxRotation: 45,
                        minRotation: 45,
                        color: '#fff',
                        autoSkip: true,
                        maxTicksLimit: 10
                    },
                    grid: {
                        color: 'rgba(255, 255, 255, 0.1)'
                    }
                }
            }
        }
    });
}
