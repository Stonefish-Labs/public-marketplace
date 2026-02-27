#!/bin/bash
# Manage Ubuntu sleep/suspend/hibernate targets
set -eu
set -o pipefail

TARGETS="sleep.target suspend.target hibernate.target hybrid-sleep.target"

case "$1" in
    disable)
        echo "Disabling sleep modes..."
        for target in $TARGETS; do
            sudo systemctl mask "$target"
        done
        echo "Done. Sleep modes disabled."
        ;;
    enable)
        echo "Enabling sleep modes..."
        for target in $TARGETS; do
            sudo systemctl unmask "$target"
        done
        echo "Done. Sleep modes enabled."
        ;;
    status)
        for target in $TARGETS; do
            echo "=== $target ==="
            systemctl status "$target" 2>/dev/null | head -5
            echo
        done
        ;;
    *)
        echo "Usage: $0 {disable|enable|status}"
        echo "  disable - Mask all sleep targets (prevents sleep/suspend/hibernate)"
        echo "  enable  - Unmask all sleep targets (allows sleep/suspend/hibernate)"
        echo "  status  - Show current status of all sleep targets"
        exit 1
        ;;
esac

