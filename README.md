# DNS Proxy with Domain Blocking

> [!WARNING]
> **Maintenance Notice:** This project is archived and is no longer being maintained. It is provided as-is for educational or historical purposes.
>
## Overview
A lightweight **DNS proxy** written in Python that intercepts DNS queries, blocks requests for domains listed in a filter file, and forwards all other queries to **Cloudflare DNS (1.1.1.1)**. The proxy prints color‑coded logs to the console, works on Windows (enables ANSI colour codes) and Linux, and can run as a simple UDP server on port 53.

## Features
- **Domain blocking** – Load a large blocklist (`filters.txt`) and return `0.0.0.0` for any matching domain.
- **Pass‑through** – All other queries are proxied to Cloudflare and the original response is returned.
- **Threaded handling** – Each request is processed in its own daemon thread, ensuring the proxy stays responsive.
- **Colored logging** – Easy to see blocked (`[BLOCK]` – red), allowed (`[PASS]` – green) and error messages.
- **Cross‑platform** – Works on Windows (enables `color` command) and Unix‑like systems.

## Prerequisites
- Python **3.8+**
- `dnslib` library

Install the dependency via:
```bash
pip install dnslib
```

> ⚠️ The proxy needs permission to bind to port **53**. On Windows you must run the script **as Administrator**, or use a higher, non‑privileged port (e.g., 5353) and adjust the `HOST`/`PORT` constants.

## Installation
1. Clone or copy the repository.
2. Ensure `filters.txt` (your blocklist) is placed in the same directory as `dns_proxy.py`.
3. Install the required Python package:
   ```bash
   pip install -r requirements.txt   # if a requirements file exists
   # or simply:
   pip install dnslib
   ```

## Usage
Run the proxy with:
```bash
python dns_proxy.py
```
You should see something like:
```
[*] Loaded 12345 blocked domains from filters.txt
[*] Starting DNS proxy on 127.0.0.1:53
```
The proxy will now listen for DNS queries. Adjust your system/network DNS settings to point to `127.0.0.1` (or the host you configured).

### Changing Host/Port
Edit the `HOST` and `PORT` variables in the `main()` function:
```python
HOST = '0.0.0.0'   # listen on all interfaces
PORT = 53          # default DNS port
```

## Configuration – `filters.txt`
- Each line should contain a single domain (e.g., `example.com`).
- Blank lines and lines starting with `#` are ignored.
- The file is loaded once at startup; restart the proxy to apply changes.

## Logging
- **[BLOCK]** – Red text, domain was blocked and answered with `0.0.0.0`.
- **[PASS]** – Green text, domain was forwarded to Cloudflare.
- Errors are suppressed to keep the service stable; uncomment the `print` line in the exception handler for debugging malformed packets.

## Security & Limitations
- The proxy does **not** implement DNSSEC or caching.
- It only handles **A** records (IPv4) in the blocked response; other record types are forwarded unchanged.
- Large blocklists may incur a slight start‑up cost while loading into memory.

## License
This project is released under the no licensce

## Contributing
1. Fork the repository.
2. Create a feature or bug‑fix branch.
3. Submit a pull request with a clear description of the changes.
4. Ensure the code follows the existing style (PEP 8) and runs without errors.

---
*Happy DNS filtering!*
