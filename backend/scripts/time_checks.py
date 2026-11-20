"""Time per check: how long start-up takes and how long one POST /api/check takes.

    python scripts/time_checks.py                                  # this computer (starts the app here)
    python scripts/time_checks.py --url https://<space>.hf.space   # a running server, e.g. the Space (Day 8)

Sends the 16 sample photos in tests/samples --rounds times (default 3) and prints the median, fastest and slowest
time per check, and the server's own split (photo check / CLIP / search). Copy the numbers into docs/PROGRESS.md.
Close other heavy programs and plug in the charger first: the numbers depend on how busy the computer is.
"""

import argparse
import os
import platform
import statistics
import sys
import time
from pathlib import Path

BACKEND = Path(__file__).resolve().parents[1]
SAMPLES = BACKEND / "tests" / "samples"
PARTS = ["read", "photo_check", "embed", "search", "total"]


def cpu_name():
    try:
        if sys.platform == "win32":
            import winreg
            key = winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, r"HARDWARE\DESCRIPTION\System\CentralProcessor\0")
            return winreg.QueryValueEx(key, "ProcessorNameString")[0].strip()
        for line in open("/proc/cpuinfo"):
            if line.startswith("model name"):
                return line.split(":", 1)[1].strip()
    except OSError:
        pass
    return platform.processor() or "unknown CPU"


def wait_until_loaded(get_health, limit=600):
    t0 = time.perf_counter()
    while time.perf_counter() - t0 < limit:
        try:
            if get_health().get("model_loaded"):
                return
        except Exception:
            pass  # server still waking up
        time.sleep(0.5)
    sys.exit("The model did not load in time.")


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--url", help="a running server, e.g. http://localhost:8000 (default: start the app here)")
    ap.add_argument("--rounds", type=int, default=3, help="how many times to send the 16 photos (default 3)")
    args = ap.parse_args()
    photos = sorted(SAMPLES.glob("*.png"))

    t0 = time.perf_counter()
    if args.url:
        import httpx
        client = httpx.Client(base_url=args.url.rstrip("/"), timeout=180)
        wait_until_loaded(lambda: client.get("/api/health").json())
        where = args.url
        startup = f"{time.perf_counter() - t0:.1f} s until model_loaded (includes waking up if the server slept)"
    else:
        sys.path.insert(0, str(BACKEND))
        import torch
        from fastapi.testclient import TestClient

        from app.main import STATE, app
        imported = time.perf_counter() - t0
        client = TestClient(app).__enter__()  # runs the real start-up (background loading + warm-up)
        wait_until_loaded(lambda: client.get("/api/health").json())
        where = f"this computer: {cpu_name()}, {os.cpu_count()} CPU threads, PyTorch uses {torch.get_num_threads()}"
        startup = (f"{time.perf_counter() - t0:.1f} s = {imported:.1f} s importing PyTorch etc. + "
                   f"{STATE.load_seconds:.1f} s loading the model and warm-up")

    wall, parts = [], {k: [] for k in PARTS}
    for _ in range(args.rounds):
        for f in photos:
            t = time.perf_counter()
            r = client.post("/api/check", files={"image": (f.name, f.read_bytes(), "image/png")})
            wall.append((time.perf_counter() - t) * 1000)
            r.raise_for_status()
            for k in PARTS:
                parts[k].append(r.json()["timing_ms"][k])

    med = statistics.median
    print(f"\nWhere:      {where}")
    print(f"Start-up:   {startup}")
    print(f"Checks:     {len(wall)} ({args.rounds} rounds x {len(photos)} sample photos, 224 x 224 PNG)")
    print(f"Per check:  median {med(wall) / 1000:.2f} s, fastest {min(wall) / 1000:.2f} s, slowest "
          f"{max(wall) / 1000:.2f} s, first {wall[0] / 1000:.2f} s (measured by the caller)")
    print("Server split (median ms): " + ", ".join(f"{k} {med(v):.0f}" for k, v in parts.items()))


if __name__ == "__main__":
    main()
