#this is a test file to practice reading a pdf
import pdfquery
import re
import shutil
import os
import tkinter as tk
from tkinter import filedialog

# globals
app_name = "invoice parser v1.0"
source_path = "<no source path currently set>"
destination_path = "<no destination path curently set>"
file_count: int = 0
file_scan_count = 0
progress_percentage = 0
files_list: list = []
current_file = "<no current file currently selected>"
last_copied_file = "n/a"
current_invoice_type = "<no invoice type currently selected>"
file_num = 0
current_file_ext_path = "<>"
current_file_ext_destination_path = "<>"
invoice_choice = ""

# file parts
new_file_name = ""
customer_name = "<no information currently parsed>"

# ---bbox coords (x0, y0, x1, y1)---
# coords for normal invoice
inv_date_normal = (394.56, 568.8, 450, 581.76)
inv_number_normal = (411.84, 583.2, 494.64, 601.92)

# coords for normal invoice
inv_date_sync = (0.0, 0.0, 0.0, 0.0)
inv_number_sync = (0.0, 0.0, 0.0, 0.0)

# coords for normal invoice
inv_date_statement = (0.0, 0.0, 0.0, 0.0)
inv_number_statement = (0.0, 0.0, 0.0, 0.0)

def update_progress_label():
    update_progress()
    label_progress.config(text="%d%% complete --- %d out of %d files scanned" %(progress_percentage, file_scan_count, file_count))


def get_source_path():
    global source_path
    global file_scan_count
    global file_count
    global progress_percentage
    file_scan_count = 0
    file_count = 0
    progress_percentage = 0
    print("get_source_path: %s" %source_path)
    source_path = filedialog.askdirectory()
    label_source_directory.config(text="Selected source path: %s" %source_path)
    print("after grabbing directory: %s" %source_path)
    get_directory_list()
    print_file_preview()
    update_progress_label()


def get_dest_path():
    global destination_path
    destination_path = filedialog.askdirectory()
    label_dest_directory.config(text="Selected destination path: %s" %destination_path)


def get_directory_list():
    global files_list
    global file_count
    print("get_directory_list: %s" %source_path)
    files_list = os.listdir(path=source_path)
    file_count = len(files_list)


def print_file_preview():
    # change status to normal for editing
    text_file_list.config(state="normal")

    # clear the text box
    text_file_list.delete("1.0", tk.END)
    line_num = 1.0
    
    text_file_list.insert(str(line_num), "%d file(s) found in directory:\n" %len(files_list))
    line_num += 1.0
    
    for file in files_list:
        text = str(file)
        print("File %s: " %text)
        text_file_list.insert(str(line_num), "%s\n" %file)
        line_num += 1.0
    
    # change status to disabled to prevent editing
    text_file_list.config(state="disabled")
    
    
def invoice_normal_button_pressed():
    global invoice_choice
    invoice_choice = "normal"
    update_console("Changed invoice selection to: %s" %invoice_choice)
    label_invoice_choices.config(text="Invoice Type: Normal Invoices")


def invoice_sync_button_pressed():
    global invoice_choice
    invoice_choice = "sync"
    update_console("Changed invoice selection to: %s" %invoice_choice)
    label_invoice_choices.config(text="Invoice Type: Synchronized Inventory Invoices")


def invoice_statement_button_pressed():
    global invoice_choice
    invoice_choice = "statement"
    update_console("Changed invoice selection to: %s" %invoice_choice)
    label_invoice_choices.config(text="Invoice Type: Statement Invoices")


# def update_bbox_coords():
#     global bbox_cords
#     try:
#         bbox_cords["coord_x0"] = float(entry_x0.get())
#     except ValueError as e:
#         update_console("ERROR - x0: " + str(e))
    
#     try:
#         bbox_cords["coord_y0"] = float(entry_y0.get())
#     except ValueError as e:
#         update_console("ERROR - y0: " + str(e))
    
#     try:
#         bbox_cords["coord_x1"] = float(entry_x1.get())
#     except ValueError as e:
#         update_console("ERROR - x1: " + str(e))
    
#     try:
#         bbox_cords["coord_y1"] = float(entry_y1.get())
#     except ValueError as e:
#         update_console("ERROR - y1: " + str(e))
    
#     if bbox_cords["coord_x0"] == 0.0 or \
#         bbox_cords["coord_y0"] == 0.0 or \
#         bbox_cords["coord_x1"] == 0.0 or \
#         bbox_cords["coord_y1"] == 0.0:
#         update_console("Please ensure new coordinates are selected for all values.")
#         return

#     text = "Coordinates changed to:\n"
#     for key, value in bbox_cords.items():
#         text += (key + " : " + str(value) + "\n")
#     update_console(text)


def load_and_parsepdf(pdf: str) -> dict:
    pdf_path = os.path.join(source_path, current_file)
    selected_pdf = pdfquery.PDFQuery(pdf_path)
    update_console("Loading file: %s" %pdf)
    selected_pdf.load()
    
    # set up a dictionary for elements
    parsed_elements = {}

    if invoice_choice == "normal":

        date_string = selected_pdf.pq(\
            'LTTextLineHorizontal:overlaps_bbox("%d, %d, %d, %d")' \
                % (inv_date_normal[0], inv_date_normal[1], inv_date_normal[2], inv_date_normal[3])).text()
        date_string = re.findall('\\d+', date_string)
        update_console("Date is: %d%d%d" % (int(date_string[2]), int(date_string[0]), int(date_string[1])))
        parsed_elements["inv_date"] = date_string
        print(parsed_elements["inv_date"])
        
        number_string = selected_pdf.pq(\
            'LTTextLineHorizontal:overlaps_bbox("%d, %d, %d, %d")' \
                % (inv_number_normal[0], inv_number_normal[1], inv_number_normal[2], inv_number_normal[3])).text()
        numbers = re.findall('\\d+', number_string)
        update_console("Invoice number is: %s" %numbers[0])
        parsed_elements["inv_number"] = numbers[0]
        print(parsed_elements["inv_number"])
    
    elif invoice_choice == "sync":
                 
        date_string = selected_pdf.pq(\
            'LTTextLineHorizontal:in_bbox("%d, %d, %d, %d")' \
                % (inv_date_sync[0], inv_date_sync[1], inv_date_sync[2], inv_date_sync[3])).text()
        parsed_elements["inv_date"] = date_string.replace('/', '')

        parsed_elements["inv_number"] = selected_pdf.pq(\
            'LTTextLineHorizontal:in_bbox("%d, %d, %d, %d")' \
                % (inv_number_sync[0], inv_number_sync[1], inv_number_sync[2], inv_number_sync[3])).text()
    
    elif invoice_choice == "statement":
                 
        date_string = selected_pdf.pq(\
            'LTTextLineHorizontal:in_bbox("%d, %d, %d, %d")' \
                % (inv_date_statement[0], inv_date_statement[1], inv_date_statement[2], inv_date_statement[3])).text()
        parsed_elements["inv_date"] = date_string.replace('/', '')

        parsed_elements["inv_number"] = selected_pdf.pq(\
            'LTTextLineHorizontal:in_bbox("%d, %d, %d, %d")' \
                % (inv_number_statement[0], inv_number_statement[1], inv_number_statement[2], inv_number_statement[3])).text()
    
    else:
        update_console("No invoice type currently selected. Unable to parse pdf.")
        update_console("Closing file: %s" %pdf)
        selected_pdf.file.close()
        return

    # don't forget to close the pdf
    update_console("Closing file: %s" %pdf)
    selected_pdf.file.close()

    return parsed_elements


def is_pdf(file: str) -> bool:
    if file.endswith(".pdf"):
        return True
    else:
        return False


def update_progress():
    global progress_percentage
    progress_percentage = int(file_scan_count / file_count) * 100
    

def update_console(text: str):
    # change status to normal for editing
    text_console.config(state="normal")
    # append to console
    text_console.insert("1.0", text + "\n")
    # change status to disabled to prevent editing
    text_console.config(state="disabled")


def on_run():
    global current_file
    global last_copied_file
    global files_list
    global current_file_ext_path
    global current_file_ext_destination_path
    global file_num
    global file_scan_count
    # while files list > 0 ------------
    while len(files_list) > 0:
        current_file = files_list[0]
        update_console("Currently working on file: %s" %current_file)

        # check if it is a pdf - remove from files list if not
        if not is_pdf(current_file):
            update_console("Skipping to next file (%s) is not a valid pdf..." %current_file)
            files_list.remove(current_file)
            current_file = files_list[0]
        
        # load and parse the current pdf
        parsed_elements = load_and_parsepdf(current_file)
        # stop parsing files is load and parsepdf returns an empty dictionary
        if len(parsed_elements) == 0:
            break

        # copy file to destination directory
        update_console("Attempting to copy: '%s'" %current_file)
        try:
            current_file_ext_path = os.path.join(source_path, current_file)
            shutil.copy(current_file_ext_path, destination_path)
            current_file_ext_destination_path = os.path.join(destination_path, current_file)
            update_console("Copy successful.")
        except shutil.SameFileError as e:
            update_console("ERROR: " + str(e))

        # rename the freshly copied file using parsed elements
        date_part = str(parsed_elements["inv_date"][2] + parsed_elements["inv_date"][0] + parsed_elements["inv_date"][1])
        new_file_base_name = date_part + '_' + parsed_elements["inv_number"]
        new_file_fullname = new_file_base_name + ".pdf"
        
        # get new full path for new file added to destination folder
        new_file_name_ext_path = os.path.join(destination_path, new_file_fullname)
        update_console("Attempting to modify name to: %s" %new_file_fullname)

        if os.path.exists(new_file_name_ext_path):
            update_console("Filename already exists - appending new tag...")
            new_file_base_name += "-(%d)" %file_num
            new_file_fullname = new_file_base_name + ".pdf"
            new_file_name_ext_path = os.path.join(destination_path, new_file_fullname)
            file_num =+ 1
            update_console("Name given to file is: %s" %new_file_fullname)
        os.rename(current_file_ext_destination_path, new_file_name_ext_path)

        # get next file in list
        files_list.remove(current_file)
        print_file_preview()
        file_scan_count += 1
        update_progress_label()
        if len(files_list) > 0:
            current_file = files_list[0]
        # exit loop when length of files list is 0
    # ---------------------------------

# Tkinter window
window = tk.Tk(className=app_name)
window.resizable(width=False, height=False)

frame_title = tk.Frame(master=window, width=800, bg="#F4E8DD", border=10)
frame_title.pack(fill=tk.BOTH)
label_main = tk.Label(master=frame_title, text=app_name.upper(), bg="#F4E8DD", fg="black")
label_main.pack()

# frame - directory paths
frame_directories = tk.Frame(master=window, bg="#7BAFD4", borderwidth=10)
frame_directories.pack(fill=tk.BOTH)

label_source_directory = tk.Label(
    master=frame_directories,
    text="Source directory path: %s" %source_path,
    anchor="w",
    justify="left",
    borderwidth=5,
    border=5,
    bg="#7BAFD4"
)
label_dest_directory = tk.Label(
    master=frame_directories,
    text="Destination directory path: %s" %destination_path,
    anchor="w",
    justify="left",
    borderwidth=5,
    border=5,
    bg="#7BAFD4"
)

# source button
button_src_directory = tk.Button(
    master=frame_directories,
    text= "Select Source Directory",
    height= 2,
    width= 30,
    border=5,
    command=get_source_path
)
button_src_directory.pack()
label_source_directory.pack()

# destination button
button_dest_directory = tk.Button(
    master=frame_directories,
    text= "Select Destination Directory",
    height= 2,
    width= 30,
    border=5,
    command=get_dest_path
)
button_dest_directory.pack()
label_dest_directory.pack()

# file list in text box
frame_files=tk.Frame(width=100, height=100, bg="#7BAFD4", border=10)
frame_files.pack(fill=tk.BOTH)

label_file_list = tk.Label(master=frame_files, text="File List", bg="#7BAFD4")
label_file_list.pack(side=tk.LEFT)

text_file_list = tk.Text(master=frame_files, width=70, height=20, bg="#13294B", fg="white", border=3)
text_file_list.pack(side=tk.LEFT)

label_console = tk.Label(
    master=frame_files,
    text="Console Output",
    bg="#7BAFD4"
)
label_console.pack(side=tk.RIGHT)

text_console = tk.Text(
    master=frame_files,
    height=20,
    width=100,
    bg="#13294B",
    fg="white",
    state="disabled",
    border=3
)
text_console.pack(side=tk.RIGHT)

# # console display
# frame_console = tk.Frame(
#     master=window,
#     height=10,
#     bg="purple",
#     border=10
# )
# frame_console.pack(side=tk.TOP, fill=tk.BOTH)
# label_console = tk.Label(
#     master=frame_console,
#     text="Console Output"
# )
# label_console.pack(side=tk.LEFT)

# text_console = tk.Text(
#     master=frame_console,
#     height=10,
#     width=100,
#     state="disabled"
# )
# text_console.pack()

# invoice type buttons
frame_invoice_selection = tk.Frame(master=window, bg="#7BAFD4", border=10)
frame_invoice_selection.pack(fill=tk.BOTH)

label_progress = tk.Label(
    master=frame_invoice_selection,
    text="%d%% complete --- %d out of %d files scanned" %(progress_percentage, file_scan_count, len(files_list)),
    bg="#7BAFD4",
    fg="yellow"
)
label_progress.pack()

label_invoice_choices = tk.Label(
    master=frame_invoice_selection,
    text="Invoice Type: %s" %current_invoice_type,
    bg="#7BAFD4"
)
label_invoice_choices.pack()

button_invoice_normal = tk.Button(
    master=frame_invoice_selection,
    text="Normal Invoices",
    bg="#00A5AD",
    fg="black",
    width=30,
    height=2,
    command=invoice_normal_button_pressed
)
button_invoice_normal.pack()

button_invoice_sync = tk.Button(
    master=frame_invoice_selection,
    text="Sync Inventory Invoices",
    bg="#00A5AD",
    fg="black",
    width=30,
    height=2,
    command=invoice_sync_button_pressed
)
button_invoice_sync.pack()

button_invoice_statement = tk.Button(
    master=frame_invoice_selection,
    text="Statement Inventory Invoices",
    bg="#00A5AD",
    fg="black",
    width=30,
    height=2,
    command=invoice_statement_button_pressed
)
button_invoice_statement.pack()

# # coordinate boxes
# frame_coord_boxes = tk.Frame(master=window, bg="pink", border=10)
# frame_coord_boxes.pack(fill=tk.BOTH)

# label_coord_boxes = tk.Label(
#     master=frame_coord_boxes,
#     text="Enter coordinates for parser (x0,y0) and (x1, y1):"
# )
# label_coord_boxes.pack()

# label_coord_x0 = tk.Label(master=frame_coord_boxes, text="x0:")
# entry_x0 = tk.Entry(
#     master=frame_coord_boxes,
#     width=10,
#     border=3
# )
# label_coord_y0 = tk.Label(master=frame_coord_boxes, text="y0:")
# entry_y0 = tk.Entry(
#     master=frame_coord_boxes,
#     width=10,
#     border=3
# )
# label_coord_x1 = tk.Label(master=frame_coord_boxes, text="x1:")
# entry_x1 = tk.Entry(
#     master=frame_coord_boxes,
#     width=10,
#     border=3
# )
# label_coord_y1 = tk.Label(master=frame_coord_boxes, text="y1:")
# entry_y1 = tk.Entry(
#     master=frame_coord_boxes,
#     width=10,
#     border=3
# )
# label_coord_x0.pack(side=tk.LEFT)
# entry_x0.pack(side=tk.LEFT)

# label_coord_y0.pack(side=tk.LEFT)
# entry_y0.pack(side=tk.LEFT)

# label_coord_x1.pack(side=tk.LEFT)
# entry_x1.pack(side=tk.LEFT)

# label_coord_y1.pack(side=tk.LEFT)
# entry_y1.pack(side=tk.LEFT)

# button_bbox_coords = tk.Button(
#     master=frame_coord_boxes,
#     text="Save Coordinates",
#     command=update_bbox_coords
# )

# button_bbox_coords.pack(side=tk.RIGHT)

# run button
frame_run_control = tk.Frame(master=window, border=10)
frame_run_control.pack()

button_run = tk.Button(
    master=frame_run_control,
    text="Run Parser",
    bg="#00594C",
    fg="white",
    command=on_run
)
button_run.pack()

window.mainloop()
