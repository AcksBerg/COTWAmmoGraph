const symbolMap = ['circle', 'cross', 'crossRot', 'rect', 'rectRot', 'star', 'triangle'];
const colorMap = ['#FF6384', '#36A2EB', '#FFCE56', '#4BC0C0', '#9966FF', '#FF9F40', '#FFCD56', '#4BC0C0', '#36A2EB', '#FF6384', '#FF9F40', '#9966FF', '#FFCD56'];

function getIndex(caliber, map) {
    return data.findIndex(c => c.caliber === caliber) % map.length;
}

let selectedCalibers = new Set();
let xAxis = 'Damage';
let yAxis = 'PenetrationPower';

function saveSelectedCalibers() {
    localStorage.setItem('selectedCalibers', JSON.stringify(Array.from(selectedCalibers)));
}

function loadSelectedCalibers() {
    const savedCalibers = localStorage.getItem('selectedCalibers');
    if (savedCalibers) {
        selectedCalibers = new Set(JSON.parse(savedCalibers));
    }
}

function initializeChart() {
    const ammoChartCtx = document.getElementById('ammoChart').getContext('2d');
    return new Chart(ammoChartCtx, {
        type: 'scatter',
        data: {
            datasets: []
        },
        options: {
            scales: {
                x: {
                    type: 'linear',
                    position: 'bottom',
                    title: {
                        display: true,
                        text: 'Damage',
                        color: '#FFFFFF'
                    },
                    ticks: {
                        color: '#FFFFFF'
                    },
                    grid: {
                        color: '#444444'
                    }
                },
                y: {
                    type: 'linear',
                    title: {
                        display: true,
                        text: 'Penetration',
                        color: '#FFFFFF'
                    },
                    ticks: {
                        color: '#FFFFFF'
                    },
                    grid: {
                        color: '#444444'
                    }
                }
            },
            plugins: {
                legend: {
                    labels: {
                        color: '#FFFFFF'
                    }
                },
                tooltip: {
                    backgroundColor: '#333333',
                    titleColor: '#FFFFFF',
                    bodyColor: '#FFFFFF',
                    callbacks: {
                        label: function (context) {
                            const type = context.raw;
                            let label = `${type.label}:\n`;
                            label += `Damage: ${type.Damage}\n`;
                            label += `Penetration: ${type.PenetrationPower}\n`;
                            label += `Projectile Count: ${type.ProjectileCount}\n`;
                            label += `Initial Speed: ${type.InitialSpeed}\n`;
                            label += `Ricochet Chance: ${type.RicochetChance}\n`;
                            label += `Fragmentation Chance: ${type.FragmentationChance}\n`;
                            label += `Bullet Mass (g): ${type.BulletMassGram}\n`;
                            label += `Heavy Bleeding Delta: ${type.HeavyBleedingDelta}\n`;
                            label += `Light Bleeding Delta: ${type.LightBleedingDelta}\n`;
                            label += `Ammo Accuracy: ${type.ammoAccr}\n`;
                            // label += `Ammo Hear: ${type.ammoHear}\n`;
                            label += `Ammo Recoil: ${type.ammoRec}\n`;
                            return label.split('\n');
                        }
                    }
                }
            }
        },
        plugins: [{
            afterDatasetsDraw: function (chart) {
                if (yAxis === 'PenetrationPower') {
                    const ctx = chart.ctx;
                    chart.data.datasets.forEach(function (dataset, i) {
                        const meta = chart.getDatasetMeta(i);
                        if (!meta.hidden) {
                            meta.data.forEach(function (element, index) {
                                ctx.fillStyle = 'rgb(255, 255, 255)';
                                const fontSize = 12;
                                const fontStyle = 'normal';
                                const fontFamily = 'Helvetica Neue';
                                ctx.font = Chart.helpers.fontString(fontSize, fontStyle, fontFamily);
                                const dataString = dataset.data[index].label;
                                const padding = 5;
                                const position = element.tooltipPosition();
                                ctx.fillText(dataString, position.x + padding, position.y - padding);
                            });
                        }
                    });

                    const yScale = chart.scales['y'];
                    const chartHeight = yScale.height;
                    const chartOffset = yScale.top;

                    ctx.fillStyle = 'rgb(255, 255, 255)';
                    ctx.font = Chart.helpers.fontString(12, 'normal', 'Helvetica Neue');
                    for (let i = 1; i <= 10; i++) {
                        const yPosition = yScale.getPixelForValue(i * 10);
                        if (yPosition >= chartOffset && yPosition <= chartOffset + chartHeight) {
                            ctx.fillText(`Class ${i}`, chart.width - 60, yPosition);
                        }
                    }
                }
            }
        }]
    });
}

let ammoChart;

function updateChart() {
    if (!ammoChart) return;

    const datasets = [];
    let minX = Infinity;
    let maxX = -Infinity;
    let minY = Infinity;
    let maxY = -Infinity;

    selectedCalibers.forEach(caliber => {
        const caliberData = data.find(c => c.caliber === caliber);
        if (caliberData) {
            const colorIndex = getIndex(caliber, colorMap);
            const symbolIndex = getIndex(caliber, symbolMap);

            const dataset = {
                label: caliber,
                data: caliberData.types.map(type => {
                    const xValue = parseFloat(type[xAxis]) || 0;
                    const yValue = parseFloat(type[yAxis]) || 0;

                    minX = Math.min(minX, xValue);
                    maxX = Math.max(maxX, xValue);
                    minY = Math.min(minY, yValue);
                    maxY = Math.max(maxY, yValue);

                    return {
                        x: xValue,
                        y: yValue,
                        ProjectileCount: type.ProjectileCount || 1,
                        Damage: type.Damage || 0,
                        PenetrationPower: type.PenetrationPower || 0,
                        label: type.name,
                        InitialSpeed: type.InitialSpeed || 0,
                        RicochetChance: type.RicochetChance || 0,
                        FragmentationChance: type.FragmentationChance || 0,
                        BulletMassGram: type.BulletMassGram || 0,
                        HeavyBleedingDelta: type.HeavyBleedingDelta || 0,
                        LightBleedingDelta: type.LightBleedingDelta || 0,
                        ammoAccr: type.ammoAccr || 0,
                        ammoHear: type.ammoHear || 0,
                        ammoRec: type.ammoRec || 0,
                        malf_changes: type.malf_changes || 0,
                        MalfMisfireChance: type.MalfMisfireChance || 0,
                        MisfireChance: type.MisfireChance || 0,
                        MalfFeedChance: type.MalfFeedChance || 0,
                        DurabilityBurnModificator: type.DurabilityBurnModificator || 0,
                        HeatFactor: type.HeatFactor || 0
                    };
                }),
                backgroundColor: colorMap[colorIndex],
                borderColor: colorMap[colorIndex],
                pointStyle: symbolMap[symbolIndex],
                pointRadius: 4,
                pointHoverRadius: 8
            };
            datasets.push(dataset);
        }
    });

    ammoChart.data.datasets = datasets;
    ammoChart.options.scales.x.min = minX - Math.ceil((maxX - minX) / 10);
    ammoChart.options.scales.x.max = maxX + Math.ceil((maxX - minX) / 10);
    ammoChart.options.scales.y.min = minY - Math.ceil((maxY - minY) / 10);
    ammoChart.options.scales.y.max = maxY + Math.ceil((maxY - minY) / 10);

    ammoChart.options.scales.x.title.text = xAxis;
    ammoChart.options.scales.y.title.text = yAxis;

    ammoChart.update();
}

function createCaliberButtons() {
    const caliberButtonsDiv = document.getElementById('caliberButtons');
    data.forEach((caliber, index) => {
        const colorIndex = getIndex(caliber.caliber, colorMap);
        const symbolIndex = getIndex(caliber.caliber, symbolMap);

        const button = document.createElement('button');
        button.innerHTML = `<span style="color:${colorMap[colorIndex]}; font-size: 20px;">&#9679;</span> ${caliber.caliber}`;
        button.style.color = colorMap[colorIndex];
        if (selectedCalibers.has(caliber.caliber)) {
            button.classList.add('active');
        }
        button.addEventListener('click', () => {
            if (selectedCalibers.has(caliber.caliber)) {
                selectedCalibers.delete(caliber.caliber);
                button.classList.remove('active');
            } else {
                selectedCalibers.add(caliber.caliber);
                button.classList.add('active');
            }
            saveSelectedCalibers();
            updateChart();
        });
        caliberButtonsDiv.appendChild(button);
    });
}

document.addEventListener('DOMContentLoaded', () => {
    loadSelectedCalibers();
    createCaliberButtons();
    ammoChart = initializeChart();
    updateChart();

    document.getElementById('x-axis-select').addEventListener('change', function() {
        xAxis = this.value;
        updateChart();
    });

    document.getElementById('y-axis-select').addEventListener('change', function() {
        yAxis = this.value;
        updateChart();
    });
});
