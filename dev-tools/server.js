const http = require('http');
const os = require('os');

const PORT = 3000;

function getLocalIps() {
  const interfaces = os.networkInterfaces();
  const ips = [];
  for (const name of Object.keys(interfaces)) {
    for (const iface of interfaces[name]) {
      if (iface.family === 'IPv4' && !iface.internal) {
        ips.push({ name, address: iface.address });
      }
    }
  }
  return ips;
}

const activityLogs = [];

const server = http.createServer((req, res) => {
  res.setHeader('Access-Control-Allow-Origin', '*');
  res.setHeader('Access-Control-Allow-Methods', 'GET, POST, OPTIONS');
  res.setHeader('Access-Control-Allow-Headers', 'Content-Type');

  if (req.method === 'OPTIONS') {
    res.writeHead(204);
    res.end();
    return;
  }

  const url = new URL(req.url, `http://${req.headers.host}`);

  if (url.pathname === '/api/ping' && req.method === 'POST') {
    let body = '';
    req.on('data', chunk => { body += chunk; });
    req.on('end', () => {
      let data = {};
      try { data = JSON.parse(body); } catch (e) {}
      const logEntry = {
        time: new Date().toLocaleTimeString(),
        clientIp: req.socket.remoteAddress.replace('::ffff:', ''),
        userAgent: req.headers['user-agent'] || 'Unknown',
        deviceNote: data.deviceNote || 'Device HP'
      };
      activityLogs.unshift(logEntry);
      if (activityLogs.length > 20) activityLogs.pop();
      console.log(`[PING SUCCESS] Dari IP: ${logEntry.clientIp} | Device: ${logEntry.deviceNote} @ ${logEntry.time}`);
      
      res.writeHead(200, { 'Content-Type': 'application/json' });
      res.end(JSON.stringify({ status: 'ok', message: 'Koneksi Berhasil! Sinyal diterima oleh Mac!', log: logEntry }));
    });
    return;
  }

  if (url.pathname === '/api/info') {
    res.writeHead(200, { 'Content-Type': 'application/json' });
    res.end(JSON.stringify({ logs: activityLogs, ips: getLocalIps() }));
    return;
  }

  // Serve Main HTML
  res.writeHead(200, { 'Content-Type': 'text/html; charset=utf-8' });
  res.end(`<!DOCTYPE html>
<html lang="id">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no">
  <title>Costa Ship Local Test</title>
  <style>
    :root {
      --costa-blue: #00387a;
      --costa-yellow: #fdb913;
      --bg-color: #f4f7fa;
      --card-bg: #ffffff;
      --text-dark: #1e293b;
      --green: #10b981;
    }
    * { box-sizing: border-box; margin: 0; padding: 0; font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif; }
    body { background-color: var(--bg-color); color: var(--text-dark); padding: 16px; display: flex; justify-content: center; }
    .container { width: 100%; max-width: 500px; }
    .header { background: linear-gradient(135deg, var(--costa-blue), #00224d); color: white; padding: 20px; border-radius: 16px; text-align: center; box-shadow: 0 4px 12px rgba(0,56,122,0.2); margin-bottom: 16px; }
    .header h1 { font-size: 1.35rem; margin-bottom: 6px; }
    .header p { font-size: 0.85rem; opacity: 0.9; }
    .badge { display: inline-block; background: var(--green); color: white; font-weight: bold; padding: 4px 12px; border-radius: 20px; font-size: 0.8rem; margin-top: 10px; }
    
    .card { background: var(--card-bg); border-radius: 16px; padding: 18px; margin-bottom: 16px; box-shadow: 0 2px 8px rgba(0,0,0,0.06); }
    .card h2 { font-size: 1.05rem; margin-bottom: 12px; color: var(--costa-blue); display: flex; align-items: center; gap: 8px; }
    
    .ip-box { background: #eef2ff; border: 2px dashed #6366f1; border-radius: 10px; padding: 14px; text-align: center; margin: 10px 0; }
    .ip-text { font-size: 1.3rem; font-weight: 800; color: #4338ca; letter-spacing: 0.5px; word-break: break-all; }
    .ip-alt { font-size: 0.95rem; font-weight: 600; color: #4f46e5; margin-top: 6px; }
    
    .btn { display: block; width: 100%; background: var(--costa-yellow); color: #000; border: none; padding: 14px; font-size: 1rem; font-weight: bold; border-radius: 12px; cursor: pointer; text-align: center; box-shadow: 0 3px 6px rgba(0,0,0,0.1); transition: transform 0.1s; }
    .btn:active { transform: scale(0.98); }
    
    .status-box { margin-top: 12px; padding: 12px; border-radius: 10px; font-size: 0.88rem; display: none; }
    .status-success { background: #dcfce7; color: #166534; border: 1px solid #86efac; }
    
    .logs-list { list-style: none; margin-top: 10px; font-size: 0.82rem; }
    .logs-list li { padding: 8px 10px; background: #f8fafc; border-left: 3px solid var(--green); border-radius: 4px; margin-bottom: 6px; }
    .footer { text-align: center; font-size: 0.75rem; color: #64748b; margin-top: 10px; }
  </style>
</head>
<body>
  <div class="container">
    <div class="header">
      <h1>Costa Ship Local Network</h1>
      <p>Diagnostic Test Wi-Fi CREW SME</p>
      <div class="badge">● LOCAL INTRANET READY</div>
    </div>

    <div class="card">
      <h2>📡 Alamat Akses HP</h2>
      <p style="font-size:0.88rem; line-height:1.4; color:#475569;">Buka browser di HP kamu yang terhubung ke Wi-Fi <b>CREW SME</b> dan ketik salah satu alamat di bawah:</p>
      <div class="ip-box">
        <div style="font-size:0.75rem; color:#6366f1; margin-bottom:4px;">ALAMAT IP UTAMA:</div>
        <div class="ip-text" id="primaryIp">Memuat IP...</div>
        <div class="ip-alt" id="mdnsHost">Atau: http://Mecmec.local:3000</div>
      </div>
    </div>

    <div class="card">
      <h2>📲 Uji Kirim Sinyal dari HP</h2>
      <p style="font-size:0.88rem; margin-bottom:12px; color:#475569;">Jika halaman ini dibuka di HP, tekan tombol di bawah:</p>
      <button class="btn" id="pingBtn" onclick="sendPing()">🚀 KIRIM SINYAL KE SERVER MAC</button>
      <div class="status-box" id="statusResult"></div>
    </div>

    <div class="card">
      <h2>📋 Riwayat Perangkat Terhubung</h2>
      <ul class="logs-list" id="logsList">
        <li style="border-left-color:#cbd5e1;">Menunggu sinyal masuk dari HP...</li>
      </ul>
    </div>

    <div class="footer">
      Costa Cruise Schedule System &bull; Diagnostic Tool
    </div>
  </div>

  <script>
    async function updateInfo() {
      try {
        const res = await fetch('/api/info');
        const data = await res.json();
        
        if (data.ips && data.ips.length > 0) {
          document.getElementById('primaryIp').innerText = 'http://' + data.ips[0].address + ':${PORT}';
        }
        
        const list = document.getElementById('logsList');
        if (data.logs.length === 0) {
          list.innerHTML = '<li style="border-left-color:#cbd5e1;">Menunggu sinyal masuk dari HP...</li>';
          return;
        }
        list.innerHTML = data.logs.map(l => 
          '<li><b>' + l.time + '</b> - ' + l.deviceNote + '<br><span style="color:#64748b; font-size:0.75rem;">IP Client: ' + l.clientIp + '</span></li>'
        ).join('');
      } catch (e) {}
    }

    async function sendPing() {
      const btn = document.getElementById('pingBtn');
      const status = document.getElementById('statusResult');
      btn.disabled = true;
      btn.innerText = 'Mengirim...';
      
      const isMobile = /iPhone|iPad|iPod|Android/i.test(navigator.userAgent);
      const isApple = /iPhone|iPad|iPod/i.test(navigator.userAgent);
      const deviceName = isMobile ? (isApple ? 'iPhone Crew' : 'Android Crew') : 'Mac Laptop';

      try {
        const res = await fetch('/api/ping', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ deviceNote: deviceName })
        });
        const data = await res.json();
        status.className = 'status-box status-success';
        status.style.display = 'block';
        status.innerHTML = '🎉 <b>BERHASIL!</b> ' + data.message + '<br><small>Waktu: ' + data.log.time + ' (IP: ' + data.log.clientIp + ')</small>';
        updateInfo();
      } catch (err) {
        status.className = 'status-box';
        status.style.backgroundColor = '#fee2e2';
        status.style.color = '#991b1b';
        status.style.border = '1px solid #fca5a5';
        status.style.display = 'block';
        status.innerHTML = '<b>GAGAL:</b> ' + err.message;
      } finally {
        btn.disabled = false;
        btn.innerText = '🚀 KIRIM SINYAL KE SERVER MAC';
      }
    }

    setInterval(updateInfo, 2500);
    updateInfo();
  </script>
</body>
</html>`);
});

server.listen(PORT, '0.0.0.0', () => {
  console.log(`Server updated on port ${PORT}`);
});
