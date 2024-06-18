#this is a test file to practice reading a pdf
import pdfquery
import shutil
import os
import tkinter as tk
from tkinter import filedialog

# globals
app_name = "Walgreens Invoice Parser v1.0"
source_path = "<no source path currently set>"
destination_path = "<no destination path curently set>"
file_count: int = 0
files_list: list = []
current_file = "<no current file currently selected>"
last_copied_file = "n/a"
current_invoice_type = "<no invoice type currently selected>"
file_num = 0

# file parts
new_file_name = ""
customer_name = "<no information currently parsed>"

# bbox coords
bbox_cords = {
    "coord_x0": 0.0,
    "coord_y0": 0.0,
    "coord_x1": 0.0,
    "coord_y1": 0.0
}


def get_source_path():
    global source_path
    print("get_source_path: %s" %source_path)
    source_path = filedialog.askdirectory()
    label_source_directory.config(text="Selected source path: %s" %source_path)
    print("after grabbing directory: %s" %source_path)
    get_directory_list()
    print_file_preview()


def get_dest_path():
    global destination_path
    destination_path = filedialog.askdirectory()
    label_dest_directory.config(text="Selected destination path: %s" %destination_path)


def get_directory_list():
    global files_list
    print("get_directory_list: %s" %source_path)
    files_list = os.listdir(path=source_path)


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
    
    
def invoice_1_button_pressed():
    print("inv button 1 pressed")
    current_invoice_type = "invoice 1"
    print(current_invoice_type)
    label_invoice_choices.config(text="Invoice Type: %s" %current_invoice_type)


def invoice_2_button_pressed():
    print("inv button 2 pressed")
    current_invoice_type = "invoice 2"
    print(current_invoice_type)
    label_invoice_choices.config(text="Invoice Type: %s" %current_invoice_type)


def update_bbox_coords():
    global bbox_cords
    try:
        bbox_cords["coord_x0"] = float(entry_x0.get())
    except ValueError as e:
        update_console("ERROR - x0: " + str(e))
    
    try:
        bbox_cords["coord_y0"] = float(entry_y0.get())
    except ValueError as e:
        update_console("ERROR - y0: " + str(e))
    
    try:
        bbox_cords["coord_x1"] = float(entry_x1.get())
    except ValueError as e:
        update_console("ERROR - x1: " + str(e))
    
    try:
        bbox_cords["coord_y1"] = float(entry_y1.get())
    except ValueError as e:
        update_console("ERROR - y1: " + str(e))
    
    if bbox_cords["coord_x0"] == 0.0 or \
        bbox_cords["coord_y0"] == 0.0 or \
        bbox_cords["coord_x1"] == 0.0 or \
        bbox_cords["coord_y1"] == 0.0:
        update_console("Please ensure new coordinates are selected for all values.")
        return

    text = "Coordinates changed to:\n"
    for key, value in bbox_cords.items():
        text += (key + " : " + str(value) + "\n")
    update_console(text)


def load_and_parsepdf(pdf: str) -> dict:
    pdf_path = os.path.join(source_path, current_file)
    selected_pdf = pdfquery.PDFQuery(pdf_path)
    update_console("Loading file: %s" %pdf)
    selected_pdf.load()
    
    # set up a dictionary for elements
    parsed_elements = {}

    # parsed_elements["name"] = selected_pdf.pq(\
    #     'LTTextLineHorizontal:in_bbox("%d, %d, %d, %d")' % (bbox_cords["coord_x0"], bbox_cords["coord_y0"], bbox_cords["coord_x1"], bbox_cords["coord_y1"])).text()

    #TODO remove this after testing is done
    parsed_elements["name"] = selected_pdf.pq(\
        'LTTextLineHorizontal:in_bbox("167.76, 980.64, 250.56, 990")').text()

    # don't forget to close the pdf
    update_console("Closing file: %s" %pdf)
    selected_pdf.file.close()

    return parsed_elements


def is_pdf(file: str) -> bool:
    if file.endswith(".pdf"):
        return True
    else:
        return False


def copy_file(file_to_copy: str, dest: str) -> str:
    full_file_path = os.path.join(source_path, file_to_copy)
    shutil.copy(full_file_path, dest)
    return full_file_path


def modify_file_name(file_to_rename: str, new_file_path: str, new_file_name: str):
    global file_num
    
    print("file to rename: %s" %file_to_rename)
    
    new_file = os.path.join(new_file_path, new_file_name)
    
    print("new file: %s" %new_file)
    
    if file_to_rename == new_file:
        new_file = new_file + "[%d]" %file_num
        new_file = os.path.join(new_file_path, new_file_name)
        print("new file inside if: %s" %new_file)
    
    os.rename(file_to_rename, new_file)
    file_num += 1


def update_console(text: str):
    # change status to normal for editing
    text_console.config(state="normal")
    # append to console
    text_console.insert("1.0", text + "\n")
    # change status to disabled to prevent editing
    text_console.config(state="disabled")


def on_run():
    global bbox_cords
    global current_file
    global last_copied_file
    global files_list
    # while files list > 0 ------------
    while len(files_list) > 0:
        current_file = files_list[0]
        print("Currently working on file: %s" %current_file)

        # check if it is a pdf - remove from files list if not
        if not is_pdf(current_file):
            print("Skipping to next file (%s) is not a valid pdf..." %current_file)
            files_list.remove(current_file)
            current_file = files_list[0]
    
        # copy file to destination directory
        last_copied_file = copy_file(current_file, destination_path)
        
        # load and parse the current pdf
        parsed_elements = load_and_parsepdf(current_file)

        # rename the freshly copied file using parsed elements
        new_file_name = parsed_elements["name"] + ".pdf"
        modify_file_name(last_copied_file, destination_path, new_file_name)

        # delete pdf from source directory (do not implement yet)
        # get next file in list
        files_list.remove(current_file)
        print_file_preview()
        if len(files_list) > 0:
            current_file = files_list[0]
        # exit loop when length of files list is 0
    # ---------------------------------
    pass

# Tkinter window
window = tk.Tk(className=app_name)
window.resizable(width=False, height=False)

frame_title = tk.Frame(master=window, width=800, bg="black", border=10)
frame_title.pack(fill=tk.BOTH)
label_main = tk.Label(master=frame_title, text=app_name.upper(), bg="black", fg="white")
label_main.pack()

# console display
frame_console = tk.Frame(
    master=window,
    height=10,
    bg="purple",
    border=10
)
frame_console.pack(side=tk.TOP, fill=tk.BOTH)
label_console = tk.Label(
    master=frame_console,
    text="Console Output"
)
label_console.pack(side=tk.LEFT)

text_console = tk.Text(
    master=frame_console,
    height=5,
    width=100,
    state="disabled"
)
text_console.pack()

# frame - directory paths
frame_directories = tk.Frame(master=window, bg="blue", borderwidth=10)
frame_directories.pack(fill=tk.BOTH)
label_source_directory = tk.Label(master=frame_directories, text="Source directory path: %s" %source_path, anchor="w", justify="left")
label_dest_directory = tk.Label(master=frame_directories, text="Destination directory path: %s" %destination_path, anchor="w", justify="left")

label_source_directory.pack()
label_dest_directory.pack()

# source button
button_src_directory = tk.Button(
    master=frame_directories,
    text= "Select Source Directory",
    height= 2,
    width= 30,
    command=get_source_path
)
button_src_directory.pack()

# destination button
button_dest_directory = tk.Button(
    master=frame_directories,
    text= "Select Destination Directory",
    height= 2,
    width= 30,
    command=get_dest_path
)
button_dest_directory.pack()

# file list in text box
frame_files=tk.Frame(width=100, height=100, bg="green", border=10)
frame_files.pack(fill=tk.BOTH)

label_file_list = tk.Label(master=frame_files, text="File List Preview:")
label_file_list.pack()

text_file_list = tk.Text(master=frame_files, width=80, height=11, bg="black", fg="white")
text_file_list.pack()

# invoice type buttons
frame_invoice_selection = tk.Frame(master=window, bg="yellow", border=10)
frame_invoice_selection.pack(fill=tk.BOTH)
label_invoice_choices = tk.Label(master=frame_invoice_selection, text="Invoice Type: %s" %current_invoice_type)
label_invoice_choices.pack()

button_invoice_1 = tk.Button(
    master=frame_invoice_selection,
    text="Invoice Type 1",
    command=invoice_1_button_pressed
)
button_invoice_1.pack()

button_invoice_2 = tk.Button(
    master=frame_invoice_selection,
    text="Invoice Type 2",
    command=invoice_2_button_pressed
)
button_invoice_2.pack()

# coordinate boxes
frame_coord_boxes = tk.Frame(master=window, bg="pink", border=10)
frame_coord_boxes.pack(fill=tk.BOTH)

label_coord_boxes = tk.Label(
    master=frame_coord_boxes,
    text="Enter coordinates for parser (x0,y0) and (x1, y1):"
)
label_coord_boxes.pack()

label_coord_x0 = tk.Label(master=frame_coord_boxes, text="x0:")
entry_x0 = tk.Entry(
    master=frame_coord_boxes,
    width=10,
    border=3
)
label_coord_y0 = tk.Label(master=frame_coord_boxes, text="y0:")
entry_y0 = tk.Entry(
    master=frame_coord_boxes,
    width=10,
    border=3
)
label_coord_x1 = tk.Label(master=frame_coord_boxes, text="x1:")
entry_x1 = tk.Entry(
    master=frame_coord_boxes,
    width=10,
    border=3
)
label_coord_y1 = tk.Label(master=frame_coord_boxes, text="y1:")
entry_y1 = tk.Entry(
    master=frame_coord_boxes,
    width=10,
    border=3
)
label_coord_x0.pack(side=tk.LEFT)
entry_x0.pack(side=tk.LEFT)

label_coord_y0.pack(side=tk.LEFT)
entry_y0.pack(side=tk.LEFT)

label_coord_x1.pack(side=tk.LEFT)
entry_x1.pack(side=tk.LEFT)

label_coord_y1.pack(side=tk.LEFT)
entry_y1.pack(side=tk.LEFT)

button_bbox_coords = tk.Button(
    master=frame_coord_boxes,
    text="Save Coordinates",
    command=update_bbox_coords
)

button_bbox_coords.pack(side=tk.RIGHT)

# run button
frame_run_control = tk.Frame(master=window, border=10)
frame_run_control.pack()

button_run = tk.Button(
    master=frame_run_control,
    text="Run Parser",
    bg="orange",
    fg="blue",
    command=on_run
)
button_run.pack()

window.mainloop()


#files = get_directory_list()

# path: str = filedialog.askopenfilename()

# # prompt user to select folder
# # path: str = filedialog.askdirectory()
# print(path)

# # get a full list of files in the path and store in list
# # files: list = os.listdir(path)
# # print(files)

# # grab first file in list, check if it's a pdf
# # curr_file = files[0]
# # print(curr_file)
# # file_name = str(curr_file)

# # if file_name.endswith(".pdf"):
# #     print("%s is a pdf file." %file_name)

# load pdf
# pdf = pdfquery.PDFQuery(path)
# pdf.load()

# bbox_coords = (167.76, 980.64, 250.56, 990)

# # get name on ATT bill as example
# customer_name = pdf.pq('LTTextLineHorizontal:in_bbox("%d, %d, %d, %d")' %bbox_coords).text()
# print(customer_name)