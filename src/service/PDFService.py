from fpdf import FPDF, HTMLMixin

class PDFService(FPDF, HTMLMixin):
    # pass 
    def footer(self):
        self.set_y(-15)
        self.set_font('Arial', 'I', 8)
        self.cell(0, 10, f'Page {self.page_no()}', 0, 0, 'C')

    def chapter_title(self, title):
        self.set_font('Arial', 'B', 16)
        self.cell(0, 10, title, 0, 1, 'L')
        self.ln(10)

    def chapter_body(self, body):
        self.set_font('Arial', '', 12)
        self.multi_cell(0, 10, body)
        self.ln()

# def create_pdf(filename):
#     pdf = PDF()
#     pdf.add_page()
    
#     pdf.chapter_title('Introduction')
#     body_text = 'This is a sample PDF generated using FPDF in Python.'
#     pdf.chapter_body(body_text)

#     pdf.output(filename)