import os
import platform
import subprocess
from typing import Optional

import pyautogui
from PIL import Image

from .models import WindowInfo


class ScreenshotCapture:
    """Core screenshot and window-enumeration logic."""

    def __init__(self) -> None:
        self.system = platform.system()
        pyautogui.FAILSAFE = False
        self.priority_apps = {
            "browsers": ["Google Chrome", "Safari", "Firefox", "Microsoft Edge", "Arc", "Chrome"],
            "media": ["YouTube", "Netflix", "VLC", "QuickTime Player", "IINA"],
            "development": [
                "Visual Studio Code",
                "Code",
                "Cursor",
                "Xcode",
                "Terminal",
                "iTerm2",
                "PyCharm",
                "iTerm 2",
            ],
            "communication": ["Slack", "Discord", "Zoom", "Microsoft Teams", "Teams", "Messages"],
        }

    def find_priority_window(self, context_hint: Optional[str] = None) -> Optional[WindowInfo]:
        windows = self.list_windows_macos()
        active = self.get_active_window_macos()

        if not context_hint:
            if active and self._is_relevant_window(active):
                return active
            return self._find_best_priority_window(windows)

        intent_category = self.parse_user_intent(context_hint)
        if intent_category:
            target_window = self._find_window_by_intent(windows, intent_category)
            if target_window:
                return target_window

        context_lower = context_hint.lower()
        if active and self._window_matches_context(active, context_lower):
            return active

        for window in windows:
            if self._window_matches_context(window, context_lower):
                return window

        if active and self._is_relevant_window(active):
            return active

        return self._find_best_priority_window(windows)

    def parse_user_intent(self, context: str) -> Optional[str]:
        context_lower = context.lower()
        intent_patterns = {
            "media_consumption": [
                "watching",
                "listening",
                "playing",
                "streaming",
                "video",
                "music",
                "youtube",
                "netflix",
                "spotify",
                "twitch",
                "hulu",
                "prime video",
                "what am i watching",
                "what am i listening",
                "what's playing",
            ],
            "development": [
                "coding",
                "programming",
                "debugging",
                "terminal",
                "editor",
                "cursor",
                "vscode",
                "code",
                "git",
                "github",
                "what am i coding",
                "what am i working on",
                "development",
                "project",
            ],
            "communication": [
                "chatting",
                "messaging",
                "meeting",
                "call",
                "slack",
                "discord",
                "teams",
                "zoom",
                "messages",
                "who am i talking to",
                "conversation",
            ],
            "browsing": [
                "browsing",
                "reading",
                "website",
                "web",
                "chrome",
                "safari",
                "firefox",
                "browser",
                "what am i reading",
                "what site",
                "webpage",
            ],
        }

        for intent, keywords in intent_patterns.items():
            if any(keyword in context_lower for keyword in keywords):
                return intent
        return None

    def _find_window_by_intent(self, windows: list[WindowInfo], intent: str) -> Optional[WindowInfo]:
        intent_apps = {
            "media_consumption": [
                "Google Chrome",
                "Safari",
                "Firefox",
                "YouTube",
                "Netflix",
                "Spotify",
                "VLC",
                "QuickTime Player",
                "IINA",
                "Twitch",
            ],
            "development": [
                "Cursor",
                "Visual Studio Code",
                "Code",
                "Xcode",
                "Terminal",
                "iTerm2",
                "PyCharm",
                "GitHub Desktop",
                "GitKraken",
            ],
            "communication": [
                "Slack",
                "Discord",
                "Zoom",
                "Microsoft Teams",
                "Teams",
                "Messages",
                "WhatsApp",
                "Telegram",
            ],
            "browsing": ["Google Chrome", "Safari", "Firefox", "Microsoft Edge", "Arc"],
        }

        target_apps = intent_apps.get(intent, [])
        if intent == "media_consumption":
            media_indicators = ["youtube", "netflix", "spotify", "video", "music", "playing", "stream"]
            for window in windows:
                if any(indicator in window.title.lower() for indicator in media_indicators):
                    if any(app.lower() in window.app.lower() for app in target_apps):
                        return window

        for window in windows:
            if any(app.lower() in window.app.lower() for app in target_apps):
                if self._is_relevant_window(window):
                    return window
        return None

    def _window_matches_context(self, window: WindowInfo, context_lower: str) -> bool:
        return (
            context_lower in window.title.lower()
            or context_lower in window.app.lower()
            or self._app_matches_context(window.app, context_lower)
        )

    def _app_matches_context(self, app_name: str, context_lower: str) -> bool:
        app_lower = app_name.lower()
        context_mappings = {
            "youtube": ["chrome", "safari", "firefox"],
            "netflix": ["chrome", "safari", "firefox"],
            "browser": ["chrome", "safari", "firefox", "edge", "arc"],
            "code": ["cursor", "visual studio code", "xcode", "pycharm"],
            "terminal": ["terminal", "iterm"],
            "music": ["spotify", "apple music", "youtube"],
            "video": ["vlc", "quicktime", "iina"],
        }

        for keyword, apps in context_mappings.items():
            if keyword in context_lower and any(app in app_lower for app in apps):
                return True
        return False

    def _find_best_priority_window(self, windows: list[WindowInfo]) -> Optional[WindowInfo]:
        if not windows:
            return None

        for apps in self.priority_apps.values():
            for app in apps:
                for window in windows:
                    if app.lower() in window.app.lower() and self._is_relevant_window(window):
                        return window

        relevant_windows = [w for w in windows if self._is_relevant_window(w)]
        if relevant_windows:
            return max(relevant_windows, key=lambda w: w.bounds[2] * w.bounds[3])
        return None

    def _is_relevant_window(self, window: WindowInfo) -> bool:
        _, _, w, h = window.bounds
        if w < 200 or h < 100:
            return False

        system_apps = [
            "Finder",
            "System Preferences",
            "Activity Monitor",
            "Console",
            "Keychain Access",
            "System Information",
        ]
        if any(sys_app in window.app for sys_app in system_apps):
            return False

        if not window.title or window.title in ["", " ", "Window"]:
            return False
        return True

    def capture_screen(self, region: Optional[tuple[int, int, int, int]] = None) -> Image.Image:
        return self._capture_crossplatform(region)

    def _capture_crossplatform(self, region: Optional[tuple[int, int, int, int]] = None) -> Image.Image:
        if region:
            x, y, w, h = region
            return pyautogui.screenshot(region=(x, y, w, h))
        return pyautogui.screenshot()

    def get_active_window_macos(self) -> Optional[WindowInfo]:
        try:
            script = """
            tell application "System Events"
                set frontApp to first application process whose frontmost is true
                set appName to name of frontApp
                set frontWindow to first window of frontApp
                set windowTitle to name of frontWindow
                set {x, y} to position of frontWindow
                set {w, h} to size of frontWindow
                return appName & "|" & windowTitle & "|" & x & "|" & y & "|" & w & "|" & h
            end tell
            """
            result = subprocess.run(["osascript", "-e", script], capture_output=True, text=True, check=True)
            parts = result.stdout.strip().split("|")
            if len(parts) == 6:
                app, title, x, y, w, h = parts
                return WindowInfo(id=0, title=title, app=app, bounds=(int(x), int(y), int(w), int(h)))
        except (subprocess.CalledProcessError, FileNotFoundError):
            return None
        return None

    def list_windows_macos(self) -> list[WindowInfo]:
        try:
            script = """
            set output to ""

            try
                tell application "System Events"
                    set all_processes to every application process where background only is false
                    repeat with proc in all_processes
                        set app_name to name of proc
                        try
                            repeat with w in every window of proc
                                set window_title to name of w
                                if window_title is not "" then
                                    set window_pos to position of w
                                    set window_size to size of w
                                    set window_info to app_name & "|" & window_title & "|" & (item 1 of window_pos) & "|" & (item 2 of window_pos) & "|" & (item 1 of window_size) & "|" & (item 2 of window_size)
                                    set output to output & window_info & linefeed
                                end if
                            end repeat
                        on error
                        end try
                    end repeat
                end tell
            on error errMsg
                return "Error: " & errMsg
            end try

            return output
            """

            result = subprocess.run(["osascript", "-e", script], capture_output=True, text=True, check=True)

            windows: list[WindowInfo] = []
            if result.stdout.strip():
                lines = result.stdout.strip().split("\n")
                for i, line in enumerate(lines):
                    if line.strip() and "|" in line:
                        parts = line.strip().split("|")
                        if len(parts) >= 6:
                            try:
                                app, title, x, y, w, h = parts[:6]
                                windows.append(
                                    WindowInfo(
                                        id=i,
                                        title=title.strip(),
                                        app=app.strip(),
                                        bounds=(int(x), int(y), int(w), int(h)),
                                    )
                                )
                            except (ValueError, IndexError):
                                continue
            return windows
        except subprocess.CalledProcessError:
            return []
        except Exception:
            return []
