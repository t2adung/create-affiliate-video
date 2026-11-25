"""Create the synthetic reference PDF."""
import sys

import pymupdf

with pymupdf.open() as document:
    page = document.new_page()
    page.insert_text((72, 72), "Evaporation = Liquid water becomes vapor.")
    page.insert_text((72, 100), "Condensation = Water vapor becomes liquid.")
    document.save(sys.argv[1])
