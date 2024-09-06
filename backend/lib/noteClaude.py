import enum
from typing import Generator, Tuple
import time
from pathlib import Path

import fitz  # PyMuPDF library
from PIL import Image, ImageDraw
import io
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from reportlab.lib.utils import ImageReader

class LayoutRule(enum.Enum):
    LINED = "Lined"
    GRID = "Grid"
    BLANK = "Blank"

class OptimizedPDFGenerator:
    PAGE_WIDTH: int = 1800
    PAGE_HEIGHT: int = 1080
    LINE_DIV = 30
    MATRIX = fitz.Matrix(1.5,1.5)

    def __init__(self, input_fp: str, output_fp: str, layout: LayoutRule):
        self.ip = Path(input_fp)
        self.op = Path(output_fp)
        self.layout = layout
        self.line_image = self.create_line_image()

    def create_line_image(self) -> Image.Image:
        image = Image.new('RGB', (self.PAGE_WIDTH, self.PAGE_HEIGHT), color='white')
        draw = ImageDraw.Draw(image)
        
        if self.layout != LayoutRule.BLANK:
            distance = self.PAGE_HEIGHT // self.LINE_DIV
            
            # Disegna linee orizzontali
            for y in range(distance, self.PAGE_HEIGHT, distance):
                draw.line([(0, y), (self.PAGE_WIDTH, y)], fill="#a5b4d4", width=2)
            
            # Disegna linee verticali per il layout GRID
            if self.layout == LayoutRule.GRID:
                for x in range(distance, self.PAGE_WIDTH, distance):
                    draw.line([(x, 0), (x, self.PAGE_HEIGHT)], fill="#a5b4d4", width=2)
        
        # Disegna la linea centrale e la linea di inizio pagina
        draw.line([(0, self.PAGE_HEIGHT // 2), (self.PAGE_WIDTH, self.PAGE_HEIGHT // 2)], fill="#a5b4d4", width=3)
        draw.line([(0, 2), (self.PAGE_WIDTH, 2)], fill="#a5b4d4", width=3)
        
        return image

    def page_fit_rescale(self, height: int, width: int) -> Tuple[int, int]:
        new_height = self.PAGE_HEIGHT // 2
        new_width = int((new_height / height) * width)
        return new_width, new_height

    def run(self) -> None:
        new_pdf = canvas.Canvas(str(self.op), pagesize=(self.PAGE_WIDTH, self.PAGE_HEIGHT))
        new_pdf.setPageCompression(1)

        line_image_reader = ImageReader(self.line_image)  # Create ImageReader once

        with fitz.open(self.ip) as doc:
            for page_num in range(0, len(doc), 2):
                page1 = doc.load_page(page_num)
                page2 = doc.load_page(page_num + 1) if page_num + 1 < len(doc) else None

                im1 = Image.open(io.BytesIO(page1.get_pixmap(matrix=self.MATRIX).tobytes()))
                im2 = Image.open(io.BytesIO(page2.get_pixmap(matrix=self.MATRIX).tobytes())) if page2 else Image.new("RGB", im1.size, "white")

                new_width, new_height = self.page_fit_rescale(width=im1.width, height=im1.height)

                # Draw images and line image
                new_pdf.drawImage(line_image_reader, 0, 0, self.PAGE_WIDTH, self.PAGE_HEIGHT)
                new_pdf.drawImage(ImageReader(im1), x=0, y=self.PAGE_HEIGHT - new_height, height=new_height, width=new_width)
                new_pdf.drawImage(ImageReader(im2), x=0, y=0, height=new_height, width=new_width)

                new_pdf.setLineWidth(3)
                new_pdf.line(0, self.PAGE_HEIGHT - new_height, self.PAGE_WIDTH, self.PAGE_HEIGHT - new_height)
                new_pdf.line(0, 2, self.PAGE_WIDTH, 2)

                new_pdf.showPage()

        new_pdf.save()

def main():
    generator = OptimizedPDFGenerator('input.pdf', 'output2.pdf', LayoutRule.GRID)
    start = time.time()
    generator.run()
    finish = time.time()
    print(f"Tempo di esecuzione ottimizzato: {finish-start:.2f} secondi")

if __name__ == "__main__":
    main()