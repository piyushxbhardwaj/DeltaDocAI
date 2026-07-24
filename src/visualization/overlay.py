from PIL import Image, ImageDraw, ImageFont
from typing import List, Tuple, Optional
from src.delta.comparator import DeltaItem
from src.observability.logger import logger

COLOR_MAP = {
    "Added": (34, 197, 94, 180),     # Green
    "Removed": (239, 68, 68, 180),   # Red
    "Modified": (234, 179, 8, 180),  # Yellow
    "Unchanged": (100, 116, 139, 50) # Gray
}

BORDER_MAP = {
    "Added": (34, 197, 94, 255),
    "Removed": (239, 68, 68, 255),
    "Modified": (234, 179, 8, 255),
    "Unchanged": (100, 116, 139, 100)
}

class VisualOverlayGenerator:
    """Generates visual difference overlays on document page images."""

    @staticmethod
    def draw_delta_overlay(
        base_image: Image.Image,
        delta_items: List[DeltaItem],
        revision: str = "B"
    ) -> Image.Image:
        """
        Draws colored rectangle bounding box overlays on page images.
        """
        # Convert to RGBA for transparent fill overlays
        overlay_img = base_image.convert("RGBA")
        draw_layer = Image.new("RGBA", overlay_img.size, (255, 255, 255, 0))
        draw = ImageDraw.Draw(draw_layer)

        img_w, img_h = overlay_img.size

        for item in delta_items:
            if item.change_type == "Unchanged":
                continue

            # Pick coordinate box for specified revision
            bbox = item.bbox_b if revision == "B" else item.bbox_a
            if not bbox or len(bbox) < 4:
                continue

            x0, y0, x1, y1 = bbox
            # Normalize or scale if coordinates match image dimensions
            # If coordinates are 0-1 normalized, scale up
            if max(x0, x1, y0, y1) <= 1.0:
                x0, x1 = x0 * img_w, x1 * img_w
                y0, y1 = y0 * img_h, y1 * img_h

            fill_color = COLOR_MAP.get(item.change_type, (255, 255, 255, 100))
            border_color = BORDER_MAP.get(item.change_type, (0, 0, 0, 255))

            # Draw transparent box fill
            draw.rectangle([x0, y0, x1, y1], fill=(fill_color[0], fill_color[1], fill_color[2], 60), outline=border_color, width=3)

            # Draw label tag badge
            label = f"{item.change_type}: {item.tag or item.object_type}"
            text_bg_box = [x0, max(0, y0 - 18), x0 + len(label) * 8 + 6, max(0, y0)]
            draw.rectangle(text_bg_box, fill=border_color)
            draw.text((x0 + 3, max(0, y0 - 16)), label, fill=(255, 255, 255, 255))

        # Composite drawn layer onto base image
        final_img = Image.alpha_composite(overlay_img, draw_layer)
        return final_img.convert("RGB")
