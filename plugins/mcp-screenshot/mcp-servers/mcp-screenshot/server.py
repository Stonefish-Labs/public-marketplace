#!/usr/bin/env python3

import base64
import os
import platform
import subprocess
import time
from typing import Any, Literal, Optional

from fastmcp import Context, FastMCP
from fastmcp.tools.tool import ToolResult
from mcp.types import ImageContent, TextContent

from core import ImageProcessor, ScreenshotCapture

mcp = FastMCP(name="ScreenshotServer", instructions="Smart screenshot capture server for macOS workflows.")
capture = ScreenshotCapture()
processor = ImageProcessor()


def _text_result(message: str) -> ToolResult:
    return ToolResult(content=[TextContent(type="text", text=message)])


def _image_result(image_b64: str, fmt: Literal["png", "jpeg"], message: str) -> ToolResult:
    return ToolResult(
        content=[
            ImageContent(type="image", data=image_b64, mimeType=f"image/{fmt}"),
            TextContent(type="text", text=message),
        ]
    )


async def _confirm_high_risk_capture(ctx: Any, action_label: str, details: str) -> ToolResult | None:
    result = await ctx.elicit(
        f"{action_label} will capture potentially sensitive on-screen data.\n\n{details}\n\nProceed?",
        response_type=None,
    )
    if result.action == "accept":
        return None
    if result.action == "decline":
        return _text_result("Capture declined by user.")
    return _text_result("Capture cancelled by user.")


def _activate_window(app_name: str, window_title: str) -> None:
    script = f'''
    tell application "System Events"
        tell application process "{app_name}"
            set frontmost to true
            tell window "{window_title}"
                perform action "AXRaise"
            end tell
        end tell
    end tell
    '''
    subprocess.run(["osascript", "-e", script], capture_output=True, text=True, check=True)


@mcp.tool(annotations={"readOnlyHint": True, "idempotentHint": True, "openWorldHint": False})
def check_permissions() -> dict:
    permissions = {
        "platform": platform.system(),
        "screen_recording": False,
        "accessibility": False,
        "working_features": [],
        "missing_features": [],
        "instructions": [],
    }

    if platform.system() != "Darwin":
        permissions["note"] = "Permission checks only apply to macOS"
        return permissions

    try:
        img = capture.capture_screen(region=(0, 0, 100, 100))
        if img and img.width > 0:
            permissions["screen_recording"] = True
            permissions["working_features"].extend(
                ["screenshot_smart", "screenshot_active_window", "screenshot_full", "screenshot_region"]
            )
    except Exception:
        permissions["missing_features"].append("All screenshot functionality")

    try:
        windows = capture.list_windows_macos()
        if windows:
            permissions["accessibility"] = True
            permissions["working_features"].extend(["list_windows", "screenshot_window (with window ID)"])
    except Exception:
        permissions["missing_features"].extend(["list_windows", "screenshot_window (selective)"])

    if permissions["screen_recording"] and permissions["accessibility"]:
        permissions["summary"] = "All functionality available"
    elif permissions["screen_recording"]:
        permissions["summary"] = "Core screenshot functionality works. Window listing needs Accessibility."
    else:
        permissions["summary"] = "Screen Recording permission required for basic functionality."
    return permissions


@mcp.tool(annotations={"readOnlyHint": True, "idempotentHint": False, "openWorldHint": False})
async def screenshot_smart_enhanced(
    ctx: Context,
    query: Optional[str] = None,
    auto_zoom: bool = True,
    quality_mode: Literal["overview", "readable", "detail"] = "readable",
    enhance_text: bool = True,
    format: Literal["png", "jpeg"] = "png",
) -> ToolResult:
    blocked = await _confirm_high_risk_capture(
        ctx,
        "Smart enhanced capture",
        f"Query: {query or 'none'}\nMode: {quality_mode}\nAuto-zoom: {auto_zoom}",
    )
    if blocked:
        return blocked

    try:
        target_window = capture.find_priority_window(query)
        if not target_window:
            return _text_result("No suitable window found for your query")

        try:
            _activate_window(target_window.app, target_window.title)
            time.sleep(0.3)
        except Exception:
            pass

        x, y, w, h = target_window.bounds
        image = capture.capture_screen(region=(x, y, w, h))
        zoom_info = ""

        if auto_zoom and not processor.is_image_clear(image):
            regions = processor.detect_content_regions(image)
            if regions:
                rx, ry, rw, rh = regions[0]
                zoom_image = capture.capture_screen(region=(x + rx, y + ry, rw, rh))
                if processor.is_image_clear(zoom_image):
                    image = zoom_image
                    zoom_info = f" (auto-zoomed to {rw}x{rh} region)"

        image_bytes = processor.process_image(image, quality_mode, enhance_text, format)
        image_b64 = base64.b64encode(image_bytes).decode()
        msg = f"Smart capture: {target_window.app} - {target_window.title} ({image.width}x{image.height}, {quality_mode} quality{zoom_info})"
        return _image_result(image_b64, format, msg)
    except Exception as exc:
        return _text_result(f"Enhanced smart capture failed: {exc}")


@mcp.tool(annotations={"readOnlyHint": True, "idempotentHint": False, "openWorldHint": False})
async def screenshot_smart(
    ctx: Context,
    context: Optional[str] = None,
    quality_mode: Literal["overview", "readable", "detail"] = "readable",
    enhance_text: bool = True,
    format: Literal["png", "jpeg"] = "png",
) -> ToolResult:
    blocked = await _confirm_high_risk_capture(ctx, "Smart capture", f"Context: {context or 'none'}\nMode: {quality_mode}")
    if blocked:
        return blocked

    try:
        target_window = capture.find_priority_window(context)
        if target_window:
            try:
                _activate_window(target_window.app, target_window.title)
                time.sleep(0.2)
            except Exception:
                pass

            x, y, w, h = target_window.bounds
            image = capture.capture_screen(region=(x, y, w, h))
            image_bytes = processor.process_image(image, quality_mode, enhance_text, format)
            image_b64 = base64.b64encode(image_bytes).decode()
            return _image_result(image_b64, format, f"Smart capture: {target_window.app} - {target_window.title} ({w}x{h})")

        return _text_result("No suitable window found")
    except Exception as exc:
        return _text_result(f"Smart capture failed: {exc}")


@mcp.tool(annotations={"readOnlyHint": True, "idempotentHint": False, "openWorldHint": False})
async def screenshot_full(
    ctx: Context,
    quality_mode: Literal["overview", "readable", "detail"] = "overview",
    enhance_text: bool = True,
    format: Literal["png", "jpeg"] = "png",
) -> ToolResult:
    blocked = await _confirm_high_risk_capture(ctx, "Full-screen capture", f"Mode: {quality_mode}\nFormat: {format}")
    if blocked:
        return blocked

    image = capture.capture_screen()
    image_bytes = processor.process_image(image, quality_mode, enhance_text, format)
    image_b64 = base64.b64encode(image_bytes).decode()
    return _image_result(image_b64, format, f"Full screen captured ({image.width}x{image.height})")


@mcp.tool(annotations={"readOnlyHint": True, "idempotentHint": False, "openWorldHint": False})
def screenshot_active_window(
    quality_mode: Literal["overview", "readable", "detail"] = "readable",
    enhance_text: bool = True,
    format: Literal["png", "jpeg"] = "png",
) -> ToolResult:
    if capture.system != "Darwin":
        return _text_result("Active window capture not yet implemented for this platform")

    window_info = capture.get_active_window_macos()
    if not window_info:
        return _text_result("Could not detect active window")

    x, y, w, h = window_info.bounds
    image = capture.capture_screen(region=(x, y, w, h))
    image_bytes = processor.process_image(image, quality_mode, enhance_text, format)
    image_b64 = base64.b64encode(image_bytes).decode()
    return _image_result(image_b64, format, f"Active window captured: {window_info.app} - {window_info.title} ({w}x{h})")


@mcp.tool(annotations={"readOnlyHint": True, "idempotentHint": False, "openWorldHint": False})
def screenshot_region(
    x: int,
    y: int,
    width: int,
    height: int,
    quality_mode: Literal["overview", "readable", "detail"] = "detail",
    enhance_text: bool = True,
    format: Literal["png", "jpeg"] = "png",
) -> ToolResult:
    if width <= 0 or height <= 0:
        return _text_result("Width and height must be positive")

    image = capture.capture_screen(region=(x, y, width, height))
    image_bytes = processor.process_image(image, quality_mode, enhance_text, format)
    image_b64 = base64.b64encode(image_bytes).decode()
    return _image_result(image_b64, format, f"Region captured: ({x},{y}) {width}x{height}")


@mcp.tool(annotations={"readOnlyHint": True, "idempotentHint": True, "openWorldHint": False})
def list_windows() -> dict:
    if capture.system == "Darwin":
        windows = capture.list_windows_macos()
        return {
            "windows": [
                {"id": window.id, "title": window.title, "app": window.app, "bounds": list(window.bounds)}
                for window in windows
            ],
            "count": len(windows),
            "platform": "macOS",
        }
    return {"windows": [], "count": 0, "platform": capture.system}


@mcp.tool(annotations={"readOnlyHint": False, "idempotentHint": True, "openWorldHint": False})
def activate_window(window_id: int) -> dict:
    windows = capture.list_windows_macos()
    target_window = next((window for window in windows if window.id == window_id), None)
    if not target_window:
        return {"success": False, "error": f"Window with ID {window_id} not found"}
    _activate_window(target_window.app, target_window.title)
    return {"success": True, "activated_window": {"app": target_window.app, "title": target_window.title, "id": window_id}}


@mcp.tool(annotations={"readOnlyHint": True, "idempotentHint": False, "openWorldHint": False})
async def screenshot_window(
    ctx: Context,
    window_id: int,
    quality_mode: Literal["overview", "readable", "detail"] = "readable",
    enhance_text: bool = True,
    format: Literal["png", "jpeg"] = "png",
) -> ToolResult:
    blocked = await _confirm_high_risk_capture(ctx, "Specific window capture", f"Window ID: {window_id}")
    if blocked:
        return blocked

    windows = capture.list_windows_macos()
    target_window = next((window for window in windows if window.id == window_id), None)
    if not target_window:
        return _text_result(f"Window with ID {window_id} not found")

    x, y, w, h = target_window.bounds
    image = capture.capture_screen(region=(x, y, w, h))
    image_bytes = processor.process_image(image, quality_mode, enhance_text, format)
    image_b64 = base64.b64encode(image_bytes).decode()
    return _image_result(image_b64, format, f"Window captured: {target_window.app} - {target_window.title} ({w}x{h})")


def main() -> None:
    mcp_host = os.getenv("HOST", "127.0.0.1")
    mcp_port = os.getenv("PORT", None)
    if mcp_port:
        mcp.run(port=int(mcp_port), host=mcp_host, transport="streamable-http")
    else:
        mcp.run()


if __name__ == "__main__":
    main()
