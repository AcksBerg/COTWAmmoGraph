const symbolMap = ['circle', 'cross', 'crossRot', 'rect', 'rectRot', 'star', 'triangle'];
const colorMap = ['#FF6384', '#36A2EB', '#FFCE56', '#4BC0C0', '#9966FF', '#FF9F40', '#FFCD56', '#4BC0C0', '#36A2EB', '#FF6384', '#FF9F40', '#9966FF', '#FFCD56'];

function getIndex(caliber, map) {
    return data.findIndex(c => c.caliber === caliber) % map.length;
}

let selectedCalibers = new Set();
const ammoChartCtx = document.getElementById('ammoChart').getContext('2d');
let ammoChart = new Chart(ammoChartCtx, {
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
                        label += `Damage: ${type.x}\n`;
                        label += `Penetration: ${type.y}\n`;
                        label += `Projectile Count: ${type.bulletCount}\n`;
                        label += `Initial Speed: ${type.InitialSpeed}\n`;
                        label += `Ricochet Chance: ${type.RicochetChance}\n`;
                        label += `Fragmentation Chance: ${type.FragmentationChance}\n`;
                        label += `Bullet Mass (g): ${type.BulletMassGram}\n`;
                        label += `Heavy Bleeding Delta: ${type.HeavyBleedingDelta}\n`;
                        label += `Light Bleeding Delta: ${type.LightBleedingDelta}\n`;
                        label += `Ammo Accuracy: ${type.ammoAccr}\n`;
                        label += `Ammo Recoil: ${type.ammoRec}\n`;
                        return label.split('\n');
                    }
                }
            }
        }
    },
    plugins: [{
        afterDatasetsDraw: function (chart) {
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
    }]
});

function updateChart() {
    const datasets = [];
    let minDamage = Infinity;
    let maxDamage = -Infinity;
    let minPenetration = Infinity;
    let maxPenetration = -Infinity;

    selectedCalibers.forEach(caliber => {
        const caliberData = data.find(c => c.caliber === caliber);
        if (caliberData) {
            const colorIndex = getIndex(caliber, colorMap);
            const symbolIndex = getIndex(caliber, symbolMap);

            const dataset = {
                label: caliber,
                data: caliberData.types.map(type => {
                    const damage = type.Damage;
                    const penetration = type.PenetrationPower != undefined ? type.PenetrationPower : 0;
                    const bulletCount = type.ProjectileCount != undefined ? type.ProjectileCount : 1;

                    minDamage = Math.min(minDamage, damage);
                    maxDamage = Math.max(maxDamage, damage);
                    minPenetration = Math.min(minPenetration, penetration);
                    maxPenetration = Math.max(maxPenetration, penetration);

                    return {
                        x: damage,
                        y: penetration,
                        label: type.name,
                        bulletCount: bulletCount,
                        InitialSpeed: type.InitialSpeed,
                        RicochetChance: type.RicochetChance,
                        FragmentationChance: type.FragmentationChance,
                        BulletMassGram: type.BulletMassGram,
                        HeavyBleedingDelta: type.HeavyBleedingDelta,
                        LightBleedingDelta: type.LightBleedingDelta,
                        ammoAccr: type.ammoAccr,
                        ammoRec: type.ammoRec,
                        malf_changes: type.malf_changes,
                        MalfMisfireChance: type.MalfMisfireChance,
                        MisfireChance: type.MisfireChance,
                        MalfFeedChance: type.MalfFeedChance,
                        DurabilityBurnModificator: type.DurabilityBurnModificator,
                        HeatFactor: type.HeatFactor
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
    ammoChart.options.scales.x.min = minDamage - Math.ceil((maxDamage - minDamage) / 10);
    ammoChart.options.scales.x.max = maxDamage + Math.ceil((maxDamage - minDamage) / 10);
    ammoChart.options.scales.y.min = minPenetration - Math.ceil((maxPenetration - minPenetration) / 10);
    ammoChart.options.scales.y.max = maxPenetration + Math.ceil((maxPenetration - minPenetration) / 10);
    ammoChart.update();
}

function saveSelectedCalibers() {
    localStorage.setItem('selectedCalibers', JSON.stringify(Array.from(selectedCalibers)));
}


function loadSelectedCalibers() {
    const savedCalibers = localStorage.getItem('selectedCalibers');
    if (savedCalibers) {
        selectedCalibers = new Set(JSON.parse(savedCalibers));
    }
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
    updateChart();
});
