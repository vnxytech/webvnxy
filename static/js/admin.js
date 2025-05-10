/**
 * Admin panel functionality
 */

document.addEventListener('DOMContentLoaded', function() {
    // Setup user activity pie chart if data exists
    const usersTable = document.querySelector('table tbody');
    if (usersTable) {
        const userRows = usersTable.querySelectorAll('tr');
        if (userRows.length > 0) {
            createUserStatusChart(userRows);
            createUserRolesChart(userRows);
        }
    }
    
    // Password toggle visibility
    setupPasswordToggle();
});

/**
 * Creates a chart showing active vs inactive users
 * @param {NodeList} userRows - Table rows containing user data
 */
function createUserStatusChart(userRows) {
    // Check if we have the chart container
    const chartContainer = document.createElement('div');
    chartContainer.className = 'col-md-6 mt-4';
    chartContainer.innerHTML = `
        <div class="card">
            <div class="card-header">
                <h5><i class="fas fa-chart-pie me-2"></i>User Status</h5>
            </div>
            <div class="card-body">
                <canvas id="userStatusChart" height="200"></canvas>
            </div>
        </div>
    `;
    
    // Get parent row to append chart
    const tabPane = document.querySelector('#users-content');
    if (!tabPane) return;
    
    // Add chart container if it doesn't exist
    if (!document.getElementById('userStatusChart')) {
        // Create chart container row if it doesn't exist
        let chartRow = tabPane.querySelector('.chart-row');
        if (!chartRow) {
            chartRow = document.createElement('div');
            chartRow.className = 'row chart-row mt-4';
            tabPane.appendChild(chartRow);
        }
        
        chartRow.appendChild(chartContainer);
    }
    
    // Count active and inactive users
    let activeCount = 0;
    let inactiveCount = 0;
    
    userRows.forEach(row => {
        const statusCell = row.querySelector('td:nth-child(4)');
        if (statusCell && statusCell.textContent.trim().includes('Active')) {
            activeCount++;
        } else {
            inactiveCount++;
        }
    });
    
    // Create the chart
    const ctx = document.getElementById('userStatusChart').getContext('2d');
    new Chart(ctx, {
        type: 'pie',
        data: {
            labels: ['Active', 'Inactive'],
            datasets: [{
                data: [activeCount, inactiveCount],
                backgroundColor: [
                    'rgba(46, 204, 113, 0.7)',
                    'rgba(149, 165, 166, 0.7)'
                ],
                borderColor: 'rgba(255, 255, 255, 0.7)',
                borderWidth: 1
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
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
 * Creates a chart showing distribution of user roles
 * @param {NodeList} userRows - Table rows containing user data
 */
function createUserRolesChart(userRows) {
    // Check if we have the chart container
    const chartContainer = document.createElement('div');
    chartContainer.className = 'col-md-6 mt-4';
    chartContainer.innerHTML = `
        <div class="card">
            <div class="card-header">
                <h5><i class="fas fa-chart-pie me-2"></i>User Roles</h5>
            </div>
            <div class="card-body">
                <canvas id="userRolesChart" height="200"></canvas>
            </div>
        </div>
    `;
    
    // Get parent row to append chart
    const tabPane = document.querySelector('#users-content');
    if (!tabPane) return;
    
    // Add chart container if it doesn't exist
    if (!document.getElementById('userRolesChart')) {
        // Create chart container row if it doesn't exist
        let chartRow = tabPane.querySelector('.chart-row');
        if (!chartRow) {
            chartRow = document.createElement('div');
            chartRow.className = 'row chart-row mt-4';
            tabPane.appendChild(chartRow);
        }
        
        chartRow.appendChild(chartContainer);
    }
    
    // Count users by role
    const roleCounts = {};
    
    userRows.forEach(row => {
        const roleCell = row.querySelector('td:nth-child(3)');
        if (roleCell) {
            const roleText = roleCell.textContent.trim();
            roleCounts[roleText] = (roleCounts[roleText] || 0) + 1;
        }
    });
    
    // Prepare chart data
    const labels = Object.keys(roleCounts);
    const data = Object.values(roleCounts);
    
    // Create the chart
    const ctx = document.getElementById('userRolesChart').getContext('2d');
    new Chart(ctx, {
        type: 'pie',
        data: {
            labels: labels,
            datasets: [{
                data: data,
                backgroundColor: [
                    'rgba(231, 76, 60, 0.7)',  // Admin - red
                    'rgba(52, 152, 219, 0.7)'  // User - blue
                ],
                borderColor: 'rgba(255, 255, 255, 0.7)',
                borderWidth: 1
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
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
 * Setup password visibility toggle for password fields
 */
function setupPasswordToggle() {
    // Get all password fields
    const passwordFields = document.querySelectorAll('input[type="password"]');
    
    passwordFields.forEach((field, index) => {
        // Create toggle button
        const toggleBtn = document.createElement('button');
        toggleBtn.type = 'button';
        toggleBtn.className = 'btn btn-outline-secondary password-toggle';
        toggleBtn.innerHTML = '<i class="fas fa-eye"></i>';
        toggleBtn.setAttribute('data-target', field.id || `password-${index}`);
        
        // Ensure field has an ID
        if (!field.id) {
            field.id = `password-${index}`;
        }
        
        // Add toggle button after password field
        field.parentNode.classList.add('position-relative');
        toggleBtn.style.position = 'absolute';
        toggleBtn.style.right = '10px';
        toggleBtn.style.top = '50%';
        toggleBtn.style.transform = 'translateY(-50%)';
        toggleBtn.style.zIndex = '10';
        field.parentNode.appendChild(toggleBtn);
        
        // Add toggle functionality
        toggleBtn.addEventListener('click', function() {
            const targetId = this.getAttribute('data-target');
            const targetField = document.getElementById(targetId);
            
            if (targetField.type === 'password') {
                targetField.type = 'text';
                this.innerHTML = '<i class="fas fa-eye-slash"></i>';
            } else {
                targetField.type = 'password';
                this.innerHTML = '<i class="fas fa-eye"></i>';
            }
        });
    });
}
