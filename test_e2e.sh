#!/bin/bash
# End-to-end test: screenshot, right-click context menu, dismiss it
set -e

API="http://localhost:8100"
OUT_DIR="/home/ubuntu/screenshots"
mkdir -p "$OUT_DIR"

echo "=== Waiting for API to be ready..."
for i in $(seq 1 120); do
    if curl -s "$API/vm/status" > /dev/null 2>&1; then
        echo "API is up!"
        break
    fi
    if [ "$i" -eq 120 ]; then
        echo "TIMEOUT: API never came up"
        exit 1
    fi
    sleep 5
done

# Give the VM extra time to finish booting to desktop
echo "=== Waiting 60s for desktop to fully load..."
sleep 60

echo "=== Screenshot 1: initial desktop"
curl -s "$API/screenshot" --output "$OUT_DIR/1_desktop.png"
echo "Saved 1_desktop.png ($(stat -c%s "$OUT_DIR/1_desktop.png") bytes)"

echo "=== Moving mouse to center and right-clicking"
curl -s -X POST "$API/mouse/move" -H 'Content-Type: application/json' -d '{"x": 640, "y": 360}'
sleep 0.5
curl -s -X POST "$API/mouse/click" -H 'Content-Type: application/json' -d '{"button": 4}'
sleep 1

echo "=== Screenshot 2: right-click context menu"
curl -s "$API/screenshot" --output "$OUT_DIR/2_right_click.png"
echo "Saved 2_right_click.png ($(stat -c%s "$OUT_DIR/2_right_click.png") bytes)"

echo "=== Moving mouse away and left-clicking to dismiss"
curl -s -X POST "$API/mouse/move" -H 'Content-Type: application/json' -d '{"x": 100, "y": 100}'
sleep 0.5
curl -s -X POST "$API/mouse/click" -H 'Content-Type: application/json' -d '{"button": 1}'
sleep 1

echo "=== Screenshot 3: after dismissing menu"
curl -s "$API/screenshot" --output "$OUT_DIR/3_dismissed.png"
echo "Saved 3_dismissed.png ($(stat -c%s "$OUT_DIR/3_dismissed.png") bytes)"

echo "=== Done! Screenshots in $OUT_DIR"
ls -la "$OUT_DIR"
