    // Availabilitx Chart Example
    function drawGasCountChart(canvas, chartdata, legend=true) {

        const chart = new Chart(canvas, {
        type: 'bar',
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
                stacked: true,
                time: {
                    unit: 'time'
                },
                gridLines: {
                    display: false,
                    drawBorder: false
                },
            }],
            yAxes: [{
                stacked: true,
                ticks: {
                    beginAtZero: true,
/*                     maxTicksLimit: 20,
                    suggestedMax: 10, */
                    stepSize: 0.5,
                    callback: function(value, index, values) {
                        return number_format(value, 1, ',', '.') + ' ppm';
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
                display: legend,
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
                return datasetLabel + ' ' + number_format(tooltipItem.yLabel, 4, ',', '.') + ' ppm';
                }
            }
            }
        }
        });
        return chart;
    }
