class VitalSignsDashboard {
    constructor() {
        this.isOnline = false;
        this.lastUpdateTime = null;
        this.heartRateChart = null;
        this.bloodPressureChart = null;
        this.maxDataPoints = 20;
        
        this.initializeCharts();
        this.startDataFetching();
        this.loadHistoryData();
        
        // Update every 5 seconds
        setInterval(() => this.fetchLatestData(), 5000);
        setInterval(() => this.loadHistoryData(), 30000); // Update history every 30 seconds
    }

    initializeCharts() {
        // Heart Rate Chart
        const heartCtx = document.getElementById('heartRateChart').getContext('2d');
        this.heartRateChart = new Chart(heartCtx, {
            type: 'line',
            data: {
                labels: [],
                datasets: [{
                    label: 'Heart Rate (bpm)',
                    data: [],
                    borderColor: '#e74c3c',
                    backgroundColor: 'rgba(231, 76, 60, 0.1)',
                    borderWidth: 3,
                    fill: true,
                    tension: 0.4,
                    pointRadius: 6,
                    pointHoverRadius: 8
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                scales: {
                    y: {
                        beginAtZero: false,
                        min: 50,
                        max: 120,
                        grid: {
                            color: 'rgba(0,0,0,0.1)'
                        }
                    },
                    x: {
                        grid: {
                            color: 'rgba(0,0,0,0.1)'
                        }
                    }
                },
                plugins: {
                    legend: {
                        display: false
                    }
                },
                elements: {
                    point: {
                        backgroundColor: '#e74c3c'
                    }
                }
            }
        });

        // Blood Pressure Chart
        const bpCtx = document.getElementById('bloodPressureChart').getContext('2d');
        this.bloodPressureChart = new Chart(bpCtx, {
            type: 'line',
            data: {
                labels: [],
                datasets: [
                    {
                        label: 'Systolic',
                        data: [],
                        borderColor: '#3498db',
                        backgroundColor: 'rgba(52, 152, 219, 0.1)',
                        borderWidth: 3,
                        fill: false,
                        tension: 0.4,
                        pointRadius: 6
                    },
                    {
                        label: 'Diastolic',
                        data: [],
                        borderColor: '#2ecc71',
                        backgroundColor: 'rgba(46, 204, 113, 0.1)',
                        borderWidth: 3,
                        fill: false,
                        tension: 0.4,
                        pointRadius: 6
                    }
                ]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                scales: {
                    y: {
                        beginAtZero: false,
                        min: 40,
                        max: 180,
                        grid: {
                            color: 'rgba(0,0,0,0.1)'
                        }
                    },
                    x: {
                        grid: {
                            color: 'rgba(0,0,0,0.1)'
                        }
                    }
                },
                plugins: {
                    legend: {
                        display: true,
                        position: 'top'
                    }
                }
            }
        });
    }

    // Replace these two fetch calls in your existing dashboard.js:

// Replace these methods in your /static/dashboard.js file:

async fetchLatestData() {
    try {
        // Use absolute URL - this was likely the issue
        const response = await fetch(`${window.location.origin}/api/latest`);
        
        console.log('Fetch response status:', response.status); // Debug log
        
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        
        const data = await response.json();
        console.log('Latest data received:', data); // Debug log
        
        this.updateDashboard(data);
        this.updateConnectionStatus(true);
        
    } catch (error) {
        console.error('Error fetching latest data:', error);
        this.updateConnectionStatus(false);
    }
}

async loadHistoryData() {
    try {
        // Use absolute URL - this was likely the issue
        const response = await fetch(`${window.location.origin}/api/history?limit=20`);
        
        console.log('History response status:', response.status); // Debug log
        
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        
        const history = await response.json();
        console.log('History data received:', history); // Debug log
        
        this.updateHistoryTable(history);
        this.updateCharts(history);
        
        // Hide loading spinner
        const historyLoading = document.getElementById('historyLoading');
        const historyTable = document.getElementById('historyTable');
        
        if (historyLoading) historyLoading.style.display = 'none';
        if (historyTable) historyTable.style.display = 'table';
        
    } catch (error) {
        console.error('Error loading history:', error);
        const historyLoading = document.getElementById('historyLoading');
        if (historyLoading) {
            historyLoading.innerHTML = 
                '<i class="fas fa-exclamation-triangle"></i> Error loading history data';
        }
    }
}

    updateDashboard(data) {
        // Update vital signs display
        document.getElementById('heartRate').textContent = data.bpm || '--';
        document.getElementById('bloodPressure').textContent = 
            data.sys && data.dia ? `${data.sys}/${data.dia}` : '--/--';
        document.getElementById('temperature').textContent = 
            data.temperature ? data.temperature.toFixed(1) : '--';
        document.getElementById('oxygenSat').textContent = data.spo2 || '--';

        // Update last update time
        if (data.timestamp) {
            this.lastUpdateTime = new Date(data.timestamp);
            document.getElementById('lastUpdate').textContent = 
                this.lastUpdateTime.toLocaleTimeString();
        }

        // Show health alerts
        this.showHealthAlerts(data);
    }

    updateConnectionStatus(isOnline) {
        this.isOnline = isOnline;
        const statusIndicator = document.getElementById('statusIndicator');
        const connectionStatus = document.getElementById('connectionStatus');

        if (isOnline) {
            statusIndicator.classList.remove('offline');
            connectionStatus.textContent = 'Connected to 4Vita Device';
        } else {
            statusIndicator.classList.add('offline');
            connectionStatus.textContent = 'Connection Lost';
        }
    }

    showHealthAlerts(data) {
        const alertBanner = document.getElementById('alertBanner');
        const alertMessage = document.getElementById('alertMessage');
        
        if (data.status && data.status !== 'Normal' && data.status !== 'No data received') {
            alertMessage.textContent = `Health Alert: ${data.status}`;
            alertBanner.classList.add('show');
            
            // Add critical class for emergency conditions
            if (data.status.includes('Emergency') || data.status.includes('Crisis')) {
                alertBanner.classList.add('critical');
            } else {
                alertBanner.classList.remove('critical');
            }
        } else {
            alertBanner.classList.remove('show');
            alertBanner.classList.remove('critical');
        }
    }

    updateHistoryTable(history) {
        const tbody = document.getElementById('historyBody');
        tbody.innerHTML = '';

        history.slice(0, 10).forEach(reading => {
            const row = tbody.insertRow();
            const timestamp = new Date(reading.timestamp);
            
            row.innerHTML = `
                <td>${timestamp.toLocaleString()}</td>
                <td>${reading.bpm} bpm</td>
                <td>${reading.sys}/${reading.dia} mmHg</td>
                <td>${reading.temperature.toFixed(1)}°C</td>
                <td>${reading.spo2}%</td>
            `;
        });
    }

    updateCharts(history) {
        if (history.length === 0) return;

        // Reverse to show oldest first in charts
        const sortedHistory = history.slice().reverse();
        
        // Prepare data for charts
        const labels = [];
        const heartRateData = [];
        const systolicData = [];
        const diastolicData = [];

        sortedHistory.slice(-this.maxDataPoints).forEach(reading => {
            const time = new Date(reading.timestamp);
            labels.push(time.toLocaleTimeString());
            heartRateData.push(reading.bpm);
            systolicData.push(reading.sys);
            diastolicData.push(reading.dia);
        });

        // Update Heart Rate Chart
        this.heartRateChart.data.labels = labels;
        this.heartRateChart.data.datasets[0].data = heartRateData;
        this.heartRateChart.update('none');

        // Update Blood Pressure Chart
        this.bloodPressureChart.data.labels = labels;
        this.bloodPressureChart.data.datasets[0].data = systolicData;
        this.bloodPressureChart.data.datasets[1].data = diastolicData;
        this.bloodPressureChart.update('none');
    }

    formatTime(date) {
        return date.toLocaleTimeString([], { 
            hour: '2-digit', 
            minute: '2-digit' 
        });
    }
}

// Initialize dashboard when page loads
document.addEventListener('DOMContentLoaded', function() {
    console.log('4Vita Health Dashboard Loading...');
    const dashboard = new VitalSignsDashboard();
    
    // Add some visual feedback
    console.log('Dashboard initialized successfully!');
    
    // Handle page visibility change to pause/resume updates
    document.addEventListener('visibilitychange', function() {
        if (document.hidden) {
            console.log('Dashboard paused (tab not visible)');
        } else {
            console.log('Dashboard resumed');
            dashboard.fetchLatestData(); // Immediate update when tab becomes visible
        }
    });
});