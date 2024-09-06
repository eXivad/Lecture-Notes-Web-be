import enum
import io
import time
from typing import Generator, Tuple

from PIL import Image, ImageDraw
from fitz import Matrix
from reportlab.lib.utils import ImageReader
from reportlab.pdfgen.canvas import Canvas
import fitz

import threading


class LayoutRule(enum.Enum):
    LINED = "Lined"
    GRID = "Grid"
    BLANK = "Blank"


def export_image(image: Image) -> ImageReader:
    side_im_data = io.BytesIO()
    image.save(side_im_data, format='jpeg', optimize=True)
    side_im_data.seek(0)
    return ImageReader(side_im_data)


class AnnotatedPDFGenerator(threading.Thread):

    MATRIX_ZOOM: int = 2
    PAGE_WIDTH: int = 1800
    PAGE_HEIGHT: int = 1080
    LINE_DIV: int = 30

    def __init__(self, input_fp: str, output_fp: str, layout: LayoutRule):
        super().__init__()
        self.ip: str = input_fp
        self.op: str = output_fp
        self.layout: LayoutRule = layout
        self.line_image = self.create_line_image()

    def create_line_image(self) -> Image:
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

        new_pdf: Canvas = Canvas(
            filename=self.op,
            pagesize=(self.PAGE_WIDTH, self.PAGE_HEIGHT)
        )

        new_pdf.setPageCompression(1)
        line_image_reader = ImageReader(self.line_image)

        for im1, im2 in self.pdf_pages():

            # im1 & im2 will have same height & width
            new_width, new_height = self.page_fit_rescale(width=im1.width, height=im1.height)

            #Notes Image
            new_pdf.drawImage(line_image_reader, 0, 0, self.PAGE_WIDTH, self.PAGE_HEIGHT)

            # Draw im1
            new_pdf.drawImage(
                export_image(im1), x=0, y=self.PAGE_HEIGHT - new_height, height=new_height, width=new_width
            )

            # Draw im2
            new_pdf.drawImage(
                export_image(im2), x=0, y=0, height=new_height, width=new_width
            )

            # Draw midline & page-start divider
            new_pdf.setStrokeColor("#a5b4d4")
            new_pdf.setLineWidth(3)
            new_pdf.line(0, self.PAGE_HEIGHT - new_height, self.PAGE_WIDTH, self.PAGE_HEIGHT - new_height)
            new_pdf.line(0, 2, self.PAGE_WIDTH, 2)

            # Next page
            new_pdf.showPage()

        # Save 'er
        new_pdf.save()
        

    def pdf_pages(self) -> Generator[Tuple[Image.Image, Image.Image], None, None]:

        pdf: fitz.Document = fitz.Document(filename=self.ip)

        for i in range(0, pdf.page_count, 2):

            # Load Fitz page
            page_1, page_2 = (
                pdf.load_page(i),
                pdf.load_page(i + 1) if i + 1 < pdf.page_count else None
            )

            matrix: Matrix = Matrix(self.MATRIX_ZOOM, self.MATRIX_ZOOM)

            # Convert to Pixmap
            page_1_map, page_2_map = (
                page_1.get_pixmap(matrix=matrix),
                page_2.get_pixmap(matrix=matrix) if page_2 else None
            )

            # Generate Page 1 PIL Image
            page_1_im: Image = Image.frombytes("RGB", (page_1_map.width, page_1_map.height), page_1_map.samples)

            # Generate Page 2 PIL Image
            page_2_im: Image = (
                Image.frombytes("RGB", (page_2_map.width, page_2_map.height), page_2_map.samples)
                .resize((page_1_im.width, page_1_im.height))
                if page_2_map else
                Image.new("RGB", (page_1_map.width, page_1_map.height), "white")  # Fallback white
            )

            yield page_1_im, page_2_im

def main():
    generator = AnnotatedPDFGenerator('input.pdf', 'output.pdf', LayoutRule.GRID)
    start = time.time()
    generator.run()
    finish = time.time()
    print(f"Tempo di esecuzione: {finish-start:.2f} secondi")

if __name__ == "__main__":
    main()

