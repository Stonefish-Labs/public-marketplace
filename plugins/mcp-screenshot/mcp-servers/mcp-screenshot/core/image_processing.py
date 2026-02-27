import io
from typing import Literal

import cv2
import numpy as np
from PIL import Image, ImageEnhance, ImageFilter


class ImageProcessor:
    @staticmethod
    def detect_content_regions(image: Image.Image) -> list[tuple[int, int, int, int]]:
        img_array = np.array(image)
        if len(img_array.shape) == 3:
            img_gray = cv2.cvtColor(img_array, cv2.COLOR_RGB2GRAY)
        else:
            img_gray = img_array

        edges = cv2.Canny(img_gray, 50, 150)
        contours, _ = cv2.findContours(edges, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

        regions: list[tuple[int, int, int, int]] = []
        min_area = (image.width * image.height) * 0.05
        max_area = (image.width * image.height) * 0.8

        for contour in contours:
            x, y, w, h = cv2.boundingRect(contour)
            area = w * h
            if min_area < area < max_area and w > 100 and h > 100 and 0.3 < w / h < 3.0:
                regions.append((x, y, w, h))

        regions.sort(key=lambda r: r[2] * r[3], reverse=True)
        return regions[:3]

    @staticmethod
    def is_image_clear(image: Image.Image, threshold: float = 100.0) -> bool:
        img_array = np.array(image.convert("L"))
        laplacian = cv2.Laplacian(img_array, cv2.CV_64F)
        return laplacian.var() > threshold

    @staticmethod
    def get_quality_scale(mode: Literal["overview", "readable", "detail"], image_width: int = 0) -> float:
        base_scales = {"overview": 0.4, "readable": 0.8, "detail": 1.0}
        scale = base_scales[mode]
        if image_width > 2000:
            scale *= 0.6
        elif image_width > 1600:
            scale *= 0.75
        return min(scale, 1.0)

    @staticmethod
    def enhance_for_text(image: Image.Image) -> Image.Image:
        img_array = np.array(image)
        kernel = np.array([[-1, -1, -1], [-1, 9, -1], [-1, -1, -1]])
        sharpened = cv2.filter2D(img_array, -1, kernel)

        enhanced = Image.fromarray(sharpened)
        enhanced = ImageEnhance.Contrast(enhanced).enhance(1.2)
        return enhanced.filter(ImageFilter.UnsharpMask(radius=1, percent=150, threshold=3))

    @staticmethod
    def process_image(
        image: Image.Image,
        quality_mode: Literal["overview", "readable", "detail"],
        enhance_text: bool,
        fmt: Literal["png", "jpeg"] = "png",
    ) -> bytes:
        if enhance_text:
            image = ImageProcessor.enhance_for_text(image)

        scale = ImageProcessor.get_quality_scale(quality_mode, image.width)
        if scale < 1.0:
            image = image.resize((int(image.width * scale), int(image.height * scale)), Image.Resampling.LANCZOS)

        buffer = io.BytesIO()
        if fmt == "jpeg":
            if image.mode in ("RGBA", "LA", "P"):
                background = Image.new("RGB", image.size, (255, 255, 255))
                if image.mode == "P":
                    image = image.convert("RGBA")
                background.paste(image, mask=image.split()[-1] if image.mode == "RGBA" else None)
                image = background
            image.save(buffer, format="JPEG", quality=85, optimize=True)
        else:
            image.save(buffer, format="PNG", optimize=True)
        return buffer.getvalue()
