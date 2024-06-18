import re
from pdfminer.high_level import extract_pages, extract_text
import os
import tkinter as tk
from tkinter import filedialog, simpledialog



# prompt user for file
path: str = filedialog.askopenfilename()

for page_layout in extract_pages(path):
    for element in page_layout:
        print(element)