import io
import fitz  # PyMuPDF
from PIL import Image
from typing import List, Tuple
from src.delta.comparator import DeltaItem
from src.visualization.overlay import VisualOverlayGenerator
from src.observability.logger import logger

class DocumentRenderer:
    """Renders visual diff overlays into PNGs and annotated PDF files."""

    @staticmethod
    def render_pdf_to_images(pdf_bytes: bytes, dpi: int = 150) -> List[Image.Image]:
        try:
            doc = fitz.open(stream=pdf_bytes, filetype="pdf")
            images = []
            for page in doc:
                pix = page.get_pixmap(dpi=dpi)
                img = Image.open(io.BytesIO(pix.tobytes("png")))
                images.append(img)
            if images:
                return images
        except Exception as e:
            logger.warning(f"PyMuPDF failed to parse PDF stream ({e}). Returning fallback blank canvas.")

        # Create fallback 800x600 image canvas
        fallback_img = Image.new("RGB", (800, 600), (15, 23, 42))
        return [fallback_img]

    @staticmethod
    def create_annotated_pdf(
        original_pdf_bytes: bytes,
        delta_items: List[DeltaItem],
        revision: str = "B"
    ) -> bytes:
        """Draws annotations directly onto PyMuPDF PDF stream."""
        doc = fitz.open(stream=original_pdf_bytes, filetype="pdf")
        
        for item in delta_items:
            if item.change_type == "Unchanged":
                continue

            bbox = item.bbox_b if revision == "B" else item.bbox_a
            page_num = (item.page_b if revision == "B" else item.page_a) or 1
            if not bbox or page_num > len(doc):
                continue

            page = doc[page_num - 1]
            rect = fitz.Rect(bbox)

            if item.change_type == "Added":
                color = (0.13, 0.77, 0.36)  # Green
            elif item.change_type == "Removed":
                color = (0.93, 0.26, 0.26)  # Red
            else:
                color = (0.91, 0.70, 0.03)  # Yellow

            # Draw rectangle box
            annot = page.add_rect_annot(rect)
            annot.set_colors(stroke=color)
            annot.set_border(width=2)
            annot.set_info(title="DeltaDoc AI", content=f"{item.change_type}: {item.description}")
            annot.update()

        output_buffer = io.BytesIO()
        doc.save(output_buffer)
        return output_buffer.getvalue()

    @staticmethod
    def generate_side_by_side_overlay(
        img_a: Image.Image,
        img_b: Image.Image,
        delta_items: List[DeltaItem]
    ) -> Image.Image:
        """Combines Revision A and Revision B into a side-by-side visual diff PNG."""
        annotated_a = VisualOverlayGenerator.draw_delta_overlay(img_a, delta_items, revision="A")
        annotated_b = VisualOverlayGenerator.draw_delta_overlay(img_b, delta_items, revision="B")

        # Standardize height
        target_h = max(annotated_a.height, annotated_b.height)
        ratio_a = target_h / annotated_a.height
        ratio_b = target_h / annotated_b.height

        w_a = int(annotated_a.width * ratio_a)
        w_b = int(annotated_b.width * ratio_b)

        resized_a = annotated_a.resize((w_a, target_h), Image.Resampling.LANCZOS)
        resized_b = annotated_b.resize((w_b, target_h), Image.Resampling.LANCZOS)

        combined = Image.new("RGB", (w_a + w_b + 20, target_h), (30, 41, 59))
        combined.paste(resized_a, (0, 0))
        combined.paste(resized_b, (w_a + 20, 0))

        return combined
