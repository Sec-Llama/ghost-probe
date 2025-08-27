#!/usr/bin/env python3
import argparse, urllib.parse, socket, ssl, sys

def recv_all(sock, limit=10_000_000, timeout=8):
    sock.settimeout(timeout)
    chunks, got = [], 0
    while True:
        try:
            b = sock.recv(4096)
            if not b:
                break
            chunks.append(b)
            got += len(b)
            if got >= limit:
                break
        except socket.timeout:
            break
    return b"".join(chunks)

def split_http(resp: bytes):
    # Return (status_line, headers_dict, body_bytes)
    sep = resp.find(b"\r\n\r\n")
    if sep == -1:
        sep = resp.find(b"\n\n")
        if sep == -1:
            # no headers – treat everything as body
            return "", {}, resp
        head = resp[:sep].decode(errors="replace")
        body = resp[sep+2:]
    else:
        head = resp[:sep].decode(errors="replace")
        body = resp[sep+4:]
    lines = head.splitlines()
    status = lines[0] if lines else ""
    headers = {}
    for line in lines[1:]:
        if ":" in line:
            k, v = line.split(":", 1)
            headers[k.strip().lower()] = v.strip()
    return status, headers, body

def request_bytes(host_header: str, path: str, http11=True):
    if not path.startswith("/"):
        path = "/" + path
    lines = [
        f"GET {path} {'HTTP/1.1' if http11 else 'HTTP/1.0'}",
        f"Host: {host_header}",
        "User-Agent: url-fetch/1.1",
        "Accept: */*",
        "Connection: close",
        "", ""
    ]
    return "\r\n".join(lines).encode("ascii", "ignore")

def fetch_once(url, insecure=False, timeout=8, no_sni=False, max_bytes=10_000_000, debug=False):
    u = urllib.parse.urlparse(url)
    scheme = (u.scheme or "http").lower()
    host = u.hostname
    port = u.port or (443 if scheme == "https" else 80)
    path = (u.path or "/") + (("?" + u.query) if u.query else "")
    host_header = host if not u.port else f"{host}:{port}"

    if not host:
        raise ValueError("URL missing host")

    # open TCP
    sock = socket.create_connection((host, port), timeout=timeout)

    # wrap in TLS if needed
    used_scheme = scheme
    if scheme == "https":
        ctx = ssl.create_default_context()
        if insecure:
            ctx.check_hostname = False
            ctx.verify_mode = ssl.CERT_NONE
        try:
            ssock = ctx.wrap_socket(sock, server_hostname=(None if no_sni else host))
            if debug:
                try:
                    alpn = ssock.selected_alpn_protocol()
                except Exception:
                    alpn = None
                print(f"[debug] TLS OK (ALPN={alpn})", file=sys.stderr)
            sock = ssock
        except ssl.SSLError as e:
            # auto-fallback to HTTP on record-layer/type errors
            if debug:
                print(f"[debug] TLS failed: {e}. Falling back to plain HTTP.", file=sys.stderr)
            sock.close()
            used_scheme = "http"
            sock = socket.create_connection((host, port), timeout=timeout)

    # send request
    sock.sendall(request_bytes(host_header, path))
    resp = recv_all(sock, limit=max_bytes, timeout=timeout)
    sock.close()
    return used_scheme, resp

def absolutize(url, location):
    # Build absolute URL from Location header
    return urllib.parse.urljoin(url, location)

def main():
    ap = argparse.ArgumentParser(description="Fetch a URL (HTTP/HTTPS) with smart TLS fallback.")
    ap.add_argument("url", help="Full URL (e.g., https://1.2.3.4:443/index.html)")
    ap.add_argument("-k", "--insecure", action="store_true", help="Ignore TLS cert errors")
    ap.add_argument("-L", "--location", action="store_true", help="Follow redirects (max 5)")
    ap.add_argument("--no-sni", action="store_true", help="Disable SNI in TLS handshake")
    ap.add_argument("--timeout", type=float, default=8.0, help="Socket timeout seconds")
    ap.add_argument("--max-body", type=int, default=1000000, help="Max body bytes to print")
    ap.add_argument("--debug", action="store_true", help="Verbose debug to stderr")
    args = ap.parse_args()

    url = args.url
    hops = 0
    while True:
        used_scheme, raw = fetch_once(
            url, insecure=args.insecure, timeout=args.timeout,
            no_sni=args.no_sni, max_bytes=args.max_body, debug=args.debug
        )
        status, headers, body = split_http(raw)

        # print
        print(f"== {used_scheme.upper()} {url} ==")
        print(status)
        for k, v in headers.items():
            print(f"{k}: {v}")
        print()
        sys.stdout.buffer.write(body[:args.max_body])
        if len(body) > args.max_body:
            print(f"\n[... truncated {len(body)-args.max_body} bytes ...]")

        # handle redirects if requested
        if args.location and status.startswith("HTTP/") and any(status.endswith(code) for code in ("301", "302", "303", "307", "308")):
            loc = headers.get("location")
            if not loc or hops >= 5:
                break
            url = absolutize(url, loc)
            hops += 1
            if args.debug:
                print(f"\n[debug] following redirect to: {url}\n", file=sys.stderr)
            continue
        break

if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(f"[!] Error: {e}", file=sys.stderr)
        sys.exit(2)
