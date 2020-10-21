from PyPDF2 import PdfFileReader, PdfFileWriter

def extract(in_files, out_file, pages, exclude_pages=()):
    exclude = {}
    for page in exclude_pages:
        exclude[page] = True

    out_pdf = PdfFileWriter()

    for in_file in in_files:
        in_pdf = PdfFileReader(in_file)
        for page in pages:
            if not page in exclude:
                out_pdf.addPage(in_pdf.getPage(page - 1))

    out_pdf.write(out_file)

