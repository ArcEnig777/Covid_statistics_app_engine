// static/script.js

// Format numbers with proper spacing
function formatNumber(num) {
    if (num >= 1000000) {
        return (num / 1000000).toFixed(1) + 'M';
    } else if (num >= 1000) {
        return (num / 1000).toFixed(1) + 'K';
    }
    return num.toLocaleString();
}

// Create properly formatted chart
function createChart(data) {
    const ctx = document.getElementById('covidChart').getContext('2d');
    
    // Destroy existing chart if it exists
    if (window.covidChartInstance) {
        window.covidChartInstance.destroy();
    }
    
    window.covidChartInstance = new Chart(ctx, {
        type: 'bar',
        data: {
            labels: ['Confirmed Cases', 'Deaths', 'Recovered'],
            datasets: [
                {
                    label: data.usa.country,
                    data: [data.usa.confirmed, data.usa.deaths, data.usa.recovered],
                    backgroundColor: 'rgba(54, 162, 235, 0.8)',
                    borderColor: 'rgba(54, 162, 235, 1)',
                    borderWidth: 2,
                    borderRadius: 8,
                    borderSkipped: false,
                },
                {
                    label: data.china.country,
                    data: [data.china.confirmed, data.china.deaths, data.china.recovered],
                    backgroundColor: 'rgba(255, 99, 132, 0.8)',
                    borderColor: 'rgba(255, 99, 132, 1)',
                    borderWidth: 2,
                    borderRadius: 8,
                    borderSkipped: false,
                }
            ]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            layout: {
                padding: {
                    top: 20,
                    right: 20,
                    bottom: 20,
                    left: 20
                }
            },
            scales: {
                y: {
                    beginAtZero: true,
                    grid: {
                        color: 'rgba(0, 0, 0, 0.1)',
                        drawBorder: false
                    },
                    ticks: {
                        callback: function(value) {
                            return formatNumber(value);
                        },
                        font: {
                            size: 12,
                            family: "'Segoe UI', Tahoma, Geneva, Verdana, sans-serif"
                        },
                        color: '#666'
                    },
                    title: {
                        display: true,
                        text: 'Number of Cases',
                        font: {
                            size: 14,
                            weight: 'bold'
                        },
                        color: '#2c3e50'
                    }
                },
                x: {
                    grid: {
                        display: false
                    },
                    ticks: {
                        font: {
                            size: 13,
                            family: "'Segoe UI', Tahoma, Geneva, Verdana, sans-serif"
                        },
                        color: '#2c3e50'
                    }
                }
            },
            plugins: {
                legend: {
                    position: 'top',
                    labels: {
                        padding: 20,
                        usePointStyle: true,
                        pointStyle: 'circle',
                        font: {
                            size: 14,
                            family: "'Segoe UI', Tahoma, Geneva, Verdana, sans-serif",
                            weight: 'bold'
                        },
                        color: '#2c3e50'
                    }
                },
                title: {
                    display: true,
                    text: 'COVID-19 Data Comparison',
                    font: {
                        size: 18,
                        weight: 'bold',
                        family: "'Segoe UI', Tahoma, Geneva, Verdana, sans-serif"
                    },
                    color: '#2c3e50',
                    padding: {
                        top: 10,
                        bottom: 30
                    }
                },
                tooltip: {
                    backgroundColor: 'rgba(255, 255, 255, 0.95)',
                    titleColor: '#2c3e50',
                    bodyColor: '#2c3e50',
                    borderColor: 'rgba(0, 0, 0, 0.1)',
                    borderWidth: 1,
                    cornerRadius: 8,
                    padding: 12,
                    displayColors: true,
                    callbacks: {
                        label: function(context) {
                            const label = context.dataset.label || '';
                            const value = context.parsed.y;
                            return `${label}: ${value.toLocaleString()}`;
                        }
                    }
                }
            },
            animation: {
                duration: 1000,
                easing: 'easeOutQuart'
            }
        }
    });
}

// Load COVID data from API
async function loadCovidData() {
    try {
        const response = await fetch('/api/covid_data');
        const data = await response.json();
        
        if (data.error) {
            throw new Error(data.error);
        }
        
        // Update data cards with formatted numbers
        document.getElementById('usaCountry').textContent = data.usa.country;
        document.getElementById('usaConfirmed').textContent = data.usa.confirmed.toLocaleString();
        document.getElementById('usaDeaths').textContent = data.usa.deaths.toLocaleString();
        document.getElementById('usaRecovered').textContent = data.usa.recovered.toLocaleString();
        
        document.getElementById('chinaCountry').textContent = data.china.country;
        document.getElementById('chinaConfirmed').textContent = data.china.confirmed.toLocaleString();
        document.getElementById('chinaDeaths').textContent = data.china.deaths.toLocaleString();
        document.getElementById('chinaRecovered').textContent = data.china.recovered.toLocaleString();
        
        // Create chart with the data
        createChart(data);
        
        // Show content, hide loading
        document.getElementById('loading').style.display = 'none';
        document.getElementById('content').style.display = 'block';
        
    } catch (error) {
        document.getElementById('loading').innerHTML = 
            `<div class="error">
                <h3>Error loading COVID-19 data</h3>
                <p>${error.message}</p>
                <button class="btn" onclick="loadCovidData()">Try Again</button>
            </div>`;
    }
}

// Initialize when page loads
document.addEventListener('DOMContentLoaded', function() {
    loadCovidData();
});