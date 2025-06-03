async function fetchData() {
  const response = await fetch('/data');
  const json = await response.json();
  let content = '';
  for (const id in json) {
    const d = json[id];
    content += `<p><b>${id}</b> → Temp: ${d.temp}, HR: ${d.hr}, SpO2: ${d.spo2}, ECG: ${d.ecg}</p>, bp_sys: ${d.bp_sys}, bp_dia: ${d.bp_dia} </p>`;
  }
  document.getElementById('data').innerHTML = content;
}
setInterval(fetchData, 3000);
