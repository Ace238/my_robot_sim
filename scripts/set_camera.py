#!/usr/bin/env python3
import time
import subprocess
import sys

print("Waiting for Gazebo to start...")
time.sleep(4)  # Wait for Gazebo GUI to be ready

print("Setting camera position...")

cmd = [
    'gz', 'service', '-s', '/gui/move_to/pose',
    '--reqtype', 'gz.msgs.GUICamera',
    '--reptype', 'gz.msgs.Boolean',
    '--timeout', '3000',
    '--req', 
    'pose: {position: {x: -0.5, y: 0, z: 0.5}, orientation: {x: 0, y: 0.3, z: 0, w: 1}}'
]

result = subprocess.run(cmd, capture_output=True, text=True)

if result.returncode == 0:
    print("✓ Camera position set successfully!")
else:
    print("✗ Failed to set camera:", result.stderr)
    sys.exit(1)
