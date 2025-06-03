async function fetchData() {
  const response = await fetch('/data');
  const json = await response.json();
  let content = '';
  for (const id in json) {
    const d = json[id];
    content += `<p><b>${id}</b> → HR: ${d.hr}, BP_SYS: ${d.bp_sys}, BP_DIA: ${d.bp_dia}, Temp: ${d.temp}, SpO2: ${d.spo2}</p>`;
  }
  document.getElementById('data').innerHTML = content;
}
setInterval(fetchData, 3000);
