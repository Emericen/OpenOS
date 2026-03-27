#!/usr/bin/env bash
set -Eeuo pipefail

# OpenOS entry script — wraps upstream QEMU startup and launches the FastAPI API server.

: "${APP:="OpenOS"}"
: "${PLATFORM:="x64"}"
: "${SUPPORT:="https://github.com/Emericen/OpenOS"}"
: "${API_PORT:="8100"}"
: "${QMP_PORT:="4444"}"

# Tell upstream networking to exclude API and QMP ports from VM DNAT
HOST_PORTS="${HOST_PORTS:+$HOST_PORTS,}$API_PORT,$QMP_PORT"
export HOST_PORTS

cd /run

. start.sh      # Startup hook
. utils.sh      # Load functions
. reset.sh      # Initialize system
. server.sh     # Start webserver
. define.sh     # Define images
. install.sh    # Download image
. disk.sh       # Initialize disks
. display.sh    # Initialize graphics
. network.sh    # Initialize network
. boot.sh       # Configure boot
. proc.sh       # Initialize processor
. memory.sh     # Check available memory
. config.sh     # Configure arguments
. finish.sh     # Finish initialization

# ── Add QMP socket for API control ──────────────────────────────

ARGS+=" -chardev socket,id=qmp0,host=localhost,port=${QMP_PORT},server=on,wait=off"
ARGS+=" -mon chardev=qmp0,mode=control"

trap - ERR

version=$(qemu-system-x86_64 --version | head -n 1 | cut -d '(' -f 1 | awk '{ print $NF }')
info "Booting image${BOOT_DESC} using QEMU v$version..."

# Launch the FastAPI server in the background
info "Starting OpenOS API server on port $API_PORT..."
QMP_PORT="$QMP_PORT" /opt/openos/bin/uvicorn \
    --app-dir /opt/openos/api \
    server:app \
    --host 0.0.0.0 \
    --port "$API_PORT" &

exec qemu-system-x86_64 ${ARGS:+ $ARGS}
