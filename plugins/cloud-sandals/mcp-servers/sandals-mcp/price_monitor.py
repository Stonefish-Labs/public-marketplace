#!/usr/bin/env python3
"""
Price Monitoring System
Manages price watches and Discord webhook notifications.
"""

import json
import requests
import os
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, Optional
from tools.check_availability import AvailabilityChecker


class PriceMonitor:
    """Manages price watches and Discord notifications."""

    def __init__(self):
        self.price_watch_file = Path(__file__).parent / "price_watches.json"
        self.discord_webhook_url = os.getenv("DISCORD_WEBHOOK_URL")
        self.availability_checker = AvailabilityChecker()

    def is_enabled(self) -> bool:
        """Check if price monitoring is properly configured."""
        return bool(self.discord_webhook_url and self.discord_webhook_url.strip())

    def add_watch(
        self,
        resort_code: str,
        room_code: str,
        check_in_date: str,
        check_out_date: str,
        max_price: float,
        guests: int = 2,
        watch_name: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Add a new price watch."""
        if not self.is_enabled():
            return {
                "error": "Price monitoring not configured. Set DISCORD_WEBHOOK_URL environment variable."
            }

        watches = []
        if self.price_watch_file.exists():
            with open(self.price_watch_file, "r") as f:
                watches = json.load(f)

        watch_id = f"{resort_code}_{room_code}_{check_in_date}_{check_out_date}_{int(datetime.now().timestamp())}"

        new_watch = {
            "watch_id": watch_id,
            "watch_name": watch_name or f"{resort_code} {room_code}",
            "resort_code": resort_code,
            "room_code": room_code,
            "check_in_date": check_in_date,
            "check_out_date": check_out_date,
            "max_price": max_price,
            "guests": guests,
            "created_at": datetime.now().isoformat(),
            "last_checked": None,
            "last_price": None,
            "active": True,
        }

        watches.append(new_watch)

        with open(self.price_watch_file, "w") as f:
            json.dump(watches, f, indent=2)

        return {
            "success": True,
            "watch_id": watch_id,
            "message": f"Price watch created for {resort_code} {room_code}. Alert when price drops below ${max_price}",
        }

    def list_watches(self) -> Dict[str, Any]:
        """List all active price watches."""
        if not self.is_enabled():
            return {
                "error": "Price monitoring not configured. Set DISCORD_WEBHOOK_URL environment variable.",
                "watches": [],
                "total": 0,
            }

        if not self.price_watch_file.exists():
            return {"watches": [], "total": 0}

        with open(self.price_watch_file, "r") as f:
            watches = json.load(f)

        active_watches = [w for w in watches if w.get("active", True)]

        return {"watches": active_watches, "total": len(active_watches)}

    def remove_watch(self, watch_id: str) -> Dict[str, Any]:
        """Remove a price watch by ID."""
        if not self.is_enabled():
            return {
                "error": "Price monitoring not configured. Set DISCORD_WEBHOOK_URL environment variable."
            }

        if not self.price_watch_file.exists():
            return {"error": "No price watches found"}

        with open(self.price_watch_file, "r") as f:
            watches = json.load(f)

        for watch in watches:
            if watch["watch_id"] == watch_id:
                watch["active"] = False
                watch["removed_at"] = datetime.now().isoformat()

                with open(self.price_watch_file, "w") as f:
                    json.dump(watches, f, indent=2)

                return {
                    "success": True,
                    "message": f"Price watch {watch_id} removed",
                }

        return {"error": f"Watch ID {watch_id} not found"}

    async def check_all_watches(self) -> Dict[str, Any]:
        """Check all active price watches and send Discord notifications if prices drop."""
        if not self.is_enabled():
            return {
                "error": "Price monitoring not configured. Set DISCORD_WEBHOOK_URL environment variable."
            }

        if not self.price_watch_file.exists():
            return {"message": "No price watches to check"}

        with open(self.price_watch_file, "r") as f:
            watches = json.load(f)

        active_watches = [w for w in watches if w.get("active", True)]

        if not active_watches:
            return {"message": "No active price watches"}

        results = []
        notifications_sent = 0

        for watch in active_watches:
            result = self.availability_checker.check_availability(
                resort_code=watch["resort_code"],
                check_in=watch["check_in_date"],
                check_out=watch["check_out_date"],
                adults=watch["guests"],
            )

            if not result.get("success"):
                results.append(
                    {
                        "watch_id": watch["watch_id"],
                        "status": "error",
                        "message": result.get("error", "Unknown error"),
                    }
                )
                continue

            rooms = self.availability_checker.parse_availability_response(result)

            current_price = None
            room_available = False

            for room in rooms:
                if room.get("room_category_code") == watch["room_code"]:
                    current_price = room.get("total_price_entire_stay")
                    room_available = room.get("available", False)
                    break

            watch["last_checked"] = datetime.now().isoformat()
            watch["last_price"] = current_price

            if current_price and room_available and current_price <= watch["max_price"]:
                notification_result = self._send_discord_notification(
                    watch, current_price
                )
                if notification_result["success"]:
                    notifications_sent += 1
                    results.append(
                        {
                            "watch_id": watch["watch_id"],
                            "status": "alert_sent",
                            "current_price": current_price,
                            "target_price": watch["max_price"],
                        }
                    )
                else:
                    results.append(
                        {
                            "watch_id": watch["watch_id"],
                            "status": "alert_failed",
                            "current_price": current_price,
                            "error": notification_result.get("error"),
                        }
                    )
            else:
                results.append(
                    {
                        "watch_id": watch["watch_id"],
                        "status": "no_alert",
                        "current_price": current_price,
                        "available": room_available,
                        "target_price": watch["max_price"],
                    }
                )

        with open(self.price_watch_file, "w") as f:
            json.dump(watches, f, indent=2)

        return {
            "total_watches_checked": len(active_watches),
            "notifications_sent": notifications_sent,
            "results": results,
        }

    def _send_discord_notification(
        self, watch: Dict[str, Any], current_price: float
    ) -> Dict[str, Any]:
        """Send Discord notification for price alert."""
        if not self.discord_webhook_url:
            return {"success": False, "error": "Discord webhook URL not configured"}

        discord_message = {
            "content": (
                f"**PRICE ALERT**\n\n"
                f"**{watch['watch_name']}** is now available!\n"
                f"Resort: {watch['resort_code']}\n"
                f"Room: {watch['room_code']}\n"
                f"Dates: {watch['check_in_date']} to {watch['check_out_date']}\n"
                f"Price: ${current_price:,.2f} (Target: ${watch['max_price']:,.2f})\n"
                f"Guests: {watch['guests']}"
            )
        }

        try:
            response = requests.post(
                self.discord_webhook_url, json=discord_message, timeout=10
            )
            if response.status_code == 204:
                return {"success": True}
            else:
                return {
                    "success": False,
                    "error": f"Discord API returned status {response.status_code}",
                }
        except requests.exceptions.RequestException as e:
            return {"success": False, "error": str(e)}
