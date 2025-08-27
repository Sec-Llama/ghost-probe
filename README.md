Got it 👍 — here’s the **entire README.md content** wrapped in **one single bash code block**, so you can copy-paste it straight into a `README.md` file. I’ll keep all the Markdown formatting inside:

````bash
# ghost-probe

A simple Python 3 script to probe a given URL (HTTP or HTTPS, even on non-standard ports) and print the response headers and body, similar to `curl -i`.  

Unlike `curl`, this tool will automatically try to detect whether a port is serving HTTPS or plain HTTP. If a TLS handshake fails (e.g. because the service is not actually using TLS on that port), it will gracefully fall back to plain HTTP and still show you the response.

⚠️ **Important Notice**  
This tool is provided **for educational and defensive purposes only**.  
Use it **only against systems you own or are explicitly authorized to test** (e.g. in a controlled lab, training environment, or with written permission).  
Do **not** use it for unauthorized scanning or exploitation.

---

## ✨ Features
- Accepts a **full URL** (http/https, any port, custom paths).  
- Tries HTTPS first and **auto-falls back to HTTP** if the TLS handshake fails.  
- Option to **disable certificate validation** (`-k/--insecure`).  
- Option to **disable SNI** in TLS handshakes (`--no-sni`).  
- Option to **follow redirects** up to 5 hops (`-L`).  
- Prints **status line, headers, and body preview** to the terminal.  
- No dependencies beyond the Python standard library (`socket`, `ssl`, `urllib`).  

---

## 🛠️ Installation
```bash
git clone https://github.com/yourusername/ghost-probe.git
cd ghost-probe
chmod +x ghost_probe.py
````

Requires **Python 3.7+**.

---

## 🚀 Usage

Basic fetch:

```bash
./ghost_probe.py http://127.0.0.1:8080/
```

HTTPS with certificate checks disabled:

```bash
./ghost_probe.py https://192.168.1.1:443/ -k
```

Non-standard port:

```bash
./ghost_probe.py https://myserver.local:8443/status
```

Follow redirects like `curl -L`:

```bash
./ghost_probe.py http://test.local/ -L
```

Verbose debugging:

```bash
./ghost_probe.py https://example.com --debug
```

---

## 🔒 Responsible Use

This project is intended for **learning, troubleshooting, and defensive security validation**.
Do not run this against systems without permission.
The author(s) take no responsibility for misuse of this tool.

---

## 📜 License

MIT (see [LICENSE](LICENSE))

```

👉 In GitHub, this will render correctly because Markdown inside a bash-fenced block still shows up as Markdown text (though with monospace style).  

Do you want me to also prepare it in a way where the **installation and usage commands** render with syntax highlighting, but the rest is plain Markdown (so it looks nicer on GitHub)?
```
