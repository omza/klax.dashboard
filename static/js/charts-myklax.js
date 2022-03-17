    // Pressure Chart Example
    function drawChartLoadprofile(canvas, chartdata) {

        const chart = new Chart(canvas, {
        type: 'line',
        data: chartdata,
        options: {
            maintainAspectRatio: false,
            layout: {
                padding: {
                    left: 10,
                    right: 25,
                    top: 25,
                    bottom: 0
                }
            },
            scales: {
            xAxes: [{
                time: {
                unit: 'date'
                },
                gridLines: {
                display: false,
                drawBorder: false
                },
                ticks: {
                maxTicksLimit: 30
                }
            }],
            yAxes: [{
                ticks: {
                    beginAtZero: false,
                    maxTicksLimit: 20,
                    suggestedMax: 11000,
                    stepSize: 1,
                    callback: function(value, index, values) {
                        return number_format(value) + ' Pa';
                }
                },
                gridLines: {
                color: "rgb(234, 236, 244)",
                zeroLineColor: "rgb(234, 236, 244)",
                drawBorder: false,
                borderDash: [2],
                zeroLineBorderDash: [2]
                }
            }],
            },
            legend: {
            display: false,
            position: 'bottom'
            },
            tooltips: {
            backgroundColor: "rgb(255,255,255)",
            bodyFontColor: "#858796",
            titleMarginBottom: 10,
            titleFontColor: '#6e707e',
            titleFontSize: 14,
            borderColor: '#dddfeb',
            borderWidth: 1,
            xPadding: 15,
            yPadding: 15,
            displayColors: false,
            intersect: false,
            mode: 'index',
            caretPadding: 10,
            callbacks: {
                label: function(tooltipItem, chart) {
                var datasetLabel = chart.datasets[tooltipItem.datasetIndex].label || '';
                return datasetLabel + ' ' + number_format(tooltipItem.yLabel) + ' Pa';
                }
            }
            }
        }
        });
        return chart;
    }
    
    
    
    
    
    // Humidity Chart Example
    function drawHumidityChart(canvas, chartdata) {

        const chart = new Chart(canvas, {
        type: 'line',
        data: chartdata,
        options: {
            maintainAspectRatio: false,
            layout: {
                padding: {
                    left: 10,
                    right: 25,
                    top: 25,
                    bottom: 0
                }
            },
            scales: {
            xAxes: [{
                time: {
                unit: 'date'
                },
                gridLines: {
                display: false,
                drawBorder: false
                },
                ticks: {
                maxTicksLimit: 30
                }
            }],
            yAxes: [{
                ticks: {
                    beginAtZero: true,
                    maxTicksLimit: 10,
                    suggestedMax: 100,
                    stepSize: 10,
                    callback: function(value, index, values) {
                        return number_format(value) + ' %';
                }
                },
                gridLines: {
                color: "rgb(234, 236, 244)",
                zeroLineColor: "rgb(234, 236, 244)",
                drawBorder: false,
                borderDash: [2],
                zeroLineBorderDash: [2]
                }
            }],
            },
            legend: {
            display: false,
            position: 'bottom'
            },
            tooltips: {
            backgroundColor: "rgb(255,255,255)",
            bodyFontColor: "#858796",
            titleMarginBottom: 10,
            titleFontColor: '#6e707e',
            titleFontSize: 14,
            borderColor: '#dddfeb',
            borderWidth: 1,
            xPadding: 15,
            yPadding: 15,
            displayColors: false,
            intersect: false,
            mode: 'index',
            caretPadding: 10,
            callbacks: {
                label: function(tooltipItem, chart) {
                var datasetLabel = chart.datasets[tooltipItem.datasetIndex].label || '';
                return datasetLabel + ' ' + number_format(tooltipItem.yLabel) + ' %';
                }
            }
            }
        }
        });
        return chart;
    }

    // Temprature Chart Example
    function drawTempChart(canvas, chartdata) {

        const chart = new Chart(canvas, {
        type: 'line',
        data: chartdata,
        options: {
            maintainAspectRatio: false,
            layout: {
                padding: {
                    left: 10,
                    right: 25,
                    top: 25,
                    bottom: 0
                }
            },
            scales: {
            xAxes: [{
                time: {
                unit: 'date'
                },
                gridLines: {
                display: false,
                drawBorder: false
                },
                ticks: {
                    maxTicksLimit: 30
                }
            }],
            yAxes: [{
                ticks: {
                    beginAtZero: false,
                    maxTicksLimit: 10,
                    suggestedMax: 40,
                    stepSize: 0.1,
                    callback: function(value, index, values) {
                        return number_format(value) + ' °C';
                }
                },
                gridLines: {
                color: "rgb(234, 236, 244)",
                zeroLineColor: "rgb(234, 236, 244)",
                drawBorder: false,
                borderDash: [2],
                zeroLineBorderDash: [2]
                }
            }],
            },
            legend: {
            display: false,
            position: 'bottom'
            },
            tooltips: {
            backgroundColor: "rgb(255,255,255)",
            bodyFontColor: "#858796",
            titleMarginBottom: 10,
            titleFontColor: '#6e707e',
            titleFontSize: 14,
            borderColor: '#dddfeb',
            borderWidth: 1,
            xPadding: 15,
            yPadding: 15,
            displayColors: false,
            intersect: false,
            mode: 'index',
            caretPadding: 10,
            callbacks: {
                label: function(tooltipItem, chart) {
                var datasetLabel = chart.datasets[tooltipItem.datasetIndex].label || '';
                return datasetLabel + ' ' + number_format(tooltipItem.yLabel) + ' °C';
                }
            }
            }
        }
        });
        return chart;
    }

    // Pressure Chart Example
    function drawPresChart(canvas, chartdata) {

        const chart = new Chart(canvas, {
        type: 'line',
        data: chartdata,
        options: {
            maintainAspectRatio: false,
            layout: {
                padding: {
                    left: 10,
                    right: 25,
                    top: 25,
                    bottom: 0
                }
            },
            scales: {
            xAxes: [{
                time: {
                unit: 'date'
                },
                gridLines: {
                display: false,
                drawBorder: false
                },
                ticks: {
                maxTicksLimit: 30
                }
            }],
            yAxes: [{
                ticks: {
                    beginAtZero: false,
                    maxTicksLimit: 20,
                    suggestedMax: 11000,
                    stepSize: 1,
                    callback: function(value, index, values) {
                        return number_format(value) + ' Pa';
                }
                },
                gridLines: {
                color: "rgb(234, 236, 244)",
                zeroLineColor: "rgb(234, 236, 244)",
                drawBorder: false,
                borderDash: [2],
                zeroLineBorderDash: [2]
                }
            }],
            },
            legend: {
            display: false,
            position: 'bottom'
            },
            tooltips: {
            backgroundColor: "rgb(255,255,255)",
            bodyFontColor: "#858796",
            titleMarginBottom: 10,
            titleFontColor: '#6e707e',
            titleFontSize: 14,
            borderColor: '#dddfeb',
            borderWidth: 1,
            xPadding: 15,
            yPadding: 15,
            displayColors: false,
            intersect: false,
            mode: 'index',
            caretPadding: 10,
            callbacks: {
                label: function(tooltipItem, chart) {
                var datasetLabel = chart.datasets[tooltipItem.datasetIndex].label || '';
                return datasetLabel + ' ' + number_format(tooltipItem.yLabel) + ' Pa';
                }
            }
            }
        }
        });
        return chart;
    }
