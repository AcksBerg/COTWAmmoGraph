const symbolMap = [
  "circle",
  "cross",
  "crossRot",
  "rect",
  "rectRot",
  "star",
  "triangle",
];
const colorMap = [
  "#FF6384",
  "#36A2EB",
  "#FFCE56",
  "#4BC0C0",
  "#9966FF",
  "#FF9F40",
  "#FFCD56",
  "#4BC0C0",
  "#36A2EB",
  "#FF6384",
  "#FF9F40",
  "#9966FF",
  "#FFCD56",
];

function getIndex(caliber, map) {
  const keys = Object.keys(data);
  return keys.indexOf(caliber) % map.length;
}

let selectedCalibers = new Set();
let xAxis = "penetration";
let yAxis = "expansion";

function saveSelectedCalibers() {
  localStorage.setItem(
    "selectedCalibers",
    JSON.stringify(Array.from(selectedCalibers))
  );
}

function loadSelectedCalibers() {
  const savedCalibers = localStorage.getItem("selectedCalibers");
  if (savedCalibers) {
    selectedCalibers = new Set(JSON.parse(savedCalibers));
  }
}

function saveSelectedAxes() {
  localStorage.setItem("xAxis", xAxis);
  localStorage.setItem("yAxis", yAxis);
}

function loadSelectedAxes() {
  const savedXAxis = localStorage.getItem("xAxis");
  const savedYAxis = localStorage.getItem("yAxis");
  if (savedXAxis) xAxis = savedXAxis;
  if (savedYAxis) yAxis = savedYAxis;
}

function initializeChart() {
  const ammoChartCtx = document.getElementById("ammoChart").getContext("2d");
  return new Chart(ammoChartCtx, {
    type: "scatter",
    data: {
      datasets: [],
    },
    options: {
      scales: {
        x: {
          type: "linear",
          position: "bottom",
          title: {
            display: true,
            text: xAxis,
            color: "#FFFFFF",
          },
          ticks: {
            color: "#FFFFFF",
          },
          grid: {
            color: "#444444",
          },
        },
        y: {
          type: "linear",
          title: {
            display: true,
            text: yAxis,
            color: "#FFFFFF",
          },
          ticks: {
            color: "#FFFFFF",
          },
          grid: {
            color: "#444444",
          },
        },
      },
      plugins: {
        legend: {
          labels: {
            color: "#FFFFFF",
          },
        },
        tooltip: {
          backgroundColor: "#333333",
          titleColor: "#FFFFFF",
          bodyColor: "#FFFFFF",
          callbacks: {
            label: function (context) {
              const type = context.raw;
              return [
                `${type.label}:`,
                `Penetration: ${type.penetration}`,
                `Expansion: ${type.expansion}`,
                `Weight: ${type.weight}`,
                `Price: ${type.price}`,
                `Min Class: ${type.minClass}`,
                `Max Class: ${type.maxClass}`,
                `Range: ${type.range}`,
              ];
            },
          },
        },
      },
    },
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

  selectedCalibers.forEach((caliber) => {
    const caliberData = data[caliber];
    if (caliberData) {
      const colorIndex = getIndex(caliber, colorMap);
      const symbolIndex = getIndex(caliber, symbolMap);

      const dataset = {
        label: caliber,
        data: caliberData.map((type) => {
          const xValue = parseFloat(type[xAxis]) || 0;
          const yValue = parseFloat(type[yAxis]) || 0;

          minX = Math.min(minX, xValue);
          maxX = Math.max(maxX, xValue);
          minY = Math.min(minY, yValue);
          maxY = Math.max(maxY, yValue);

          return {
            x: xValue,
            y: yValue,
            label: type.Name,
            penetration: type.penetration,
            expansion: type.expansion,
            weight: type.weight,
            price: type.price,
            minClass: type.minClass,
            maxClass: type.maxClass,
            range: type.range,
          };
        }),
        backgroundColor: colorMap[colorIndex],
        borderColor: colorMap[colorIndex],
        pointStyle: symbolMap[symbolIndex],
        pointRadius: 4,
        pointHoverRadius: 8,
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
  const caliberButtonsDiv = document.getElementById("caliberButtons");
  Object.keys(data).forEach((caliber, index) => {
    const colorIndex = getIndex(caliber, colorMap);

    const button = document.createElement("button");
    button.innerHTML = `<span style="color:${colorMap[colorIndex]}; font-size: 20px;">&#9679;</span> ${caliber}`;
    button.style.color = colorMap[colorIndex];
    if (selectedCalibers.has(caliber)) {
      button.classList.add("active");
    }
    button.addEventListener("click", () => {
      if (selectedCalibers.has(caliber)) {
        selectedCalibers.delete(caliber);
        button.classList.remove("active");
      } else {
        selectedCalibers.add(caliber);
        button.classList.add("active");
      }
      saveSelectedCalibers();
      updateChart();
    });
    caliberButtonsDiv.appendChild(button);
  });
}

document.addEventListener("DOMContentLoaded", () => {
  loadSelectedCalibers();
  loadSelectedAxes();
  createCaliberButtons();
  ammoChart = initializeChart();
  updateChart();

  document
    .getElementById("x-axis-select")
    .addEventListener("change", function () {
      xAxis = this.value;
      saveSelectedAxes();
      updateChart();
    });

  document
    .getElementById("y-axis-select")
    .addEventListener("change", function () {
      yAxis = this.value;
      saveSelectedAxes();
      updateChart();
    });

  document.getElementById("x-axis-select").value = xAxis;
  document.getElementById("y-axis-select").value = yAxis;
});
