"""
Run after starting the service: python run.py
Usage: python scripts/smoke_flow.py
"""
import sys
import time

try:
    import httpx
except ImportError:
    print("Install httpx: pip install httpx")
    sys.exit(1)

BASE = "http://127.0.0.1:8101"


def main() -> None:
    with httpx.Client(base_url=BASE, timeout=30.0) as client:
        health = client.get("/health").json()
        print("Health:", health)

        scan = client.get("/api/v1/collars/scan").json()
        collar = scan["collars"][0]
        collar_id = collar["id"]
        print(f"Scanned collar: {collar_id} rssi={collar['rssi_dbm']}")

        client.post(f"/api/v1/collars/{collar_id}/identify", json={"blinks": 3})
        for _ in range(20):
            status = client.get(f"/api/v1/collars/{collar_id}/identify/status").json()
            print("  identify:", status["status"], status["completed_blinks"], "/", status["target_blinks"])
            if status["verified"]:
                break
            time.sleep(0.3)

        cow_id = "COW-001"
        result = client.post(
            "/api/v1/assignments/link-cow",
            json={"collar_id": collar_id, "cow_id": cow_id, "require_identify": True},
        )
        print("Assignment:", result.status_code, result.json())


if __name__ == "__main__":
    main()
