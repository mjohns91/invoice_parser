import pdfquery
import re
import shutil
import os
import time
import tkinter as tk

from tkinter import filedialog

APP_NAME: str = "invoice parser v1.0"
CYCLE_TIME: int = 100

source_path: str = "<no source path currently set>"
destination_path: str = "<no destination path currently set>"

file_count: int = 0
file_scan_count: int = 0
progress_percentage: int = 0
directory_list: list = []
current_file: str = "<no current file currently selected>"
last_copied_file: str = "<no previous file copied>"
file_num: int = 0
current_file_ext_path: str = "<no current file ext path set>"
current_file_ext_destination_path: str = "<no destination path set>"

# ---bbox coords (x0, y0, x1, y1)---
invoice_date: tuple = (394.56, 568.8, 450, 581.76)
invoice_number: tuple = (411.84, 583.2, 494.64, 601.92)


def update_progress_label():
    """Updates the GUI's progress label on a repeating cycle.
    
    """
    update_progress()
    label_progress.config(text="%d%% complete --- %d out of %d files scanned" %(progress_percentage, file_scan_count, file_count))
    window.after(CYCLE_TIME, update_progress_label)


def get_source_path():
    """Prompts user to select a source directory where files to be scanned reside.
    
    """
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
    set_directory_list()


def set_dest_path():
    """Sets the destination_path var to the selected directory provided by user prompt. This is
    set via tkinter button.
    
    """
    global destination_path
    destination_path = filedialog.askdirectory()
    label_dest_directory.config(text="Selected destination path: %s" %destination_path)


def set_directory_list():
    """Scans current directory set as source_path var and updates global directory_list var with a list
    of all files found in path. This is set via tkinter button.
    
    """
    global directory_list
    global file_count
    directory_list = os.listdir(path=source_path)
    file_count = len(directory_list)


def print_file_preview():
    """Update the GUI file preview text box. Clears the text box and prints remaining files
    in directory list.

    """
    # Change status to normal for editing
    text_file_list.config(state="normal")

    # Clear the text box
    text_file_list.delete("1.0", tk.END)
    line_num = 1.0
    
    text_file_list.insert(str(line_num), "%d file(s) found in directory:\n" %len(directory_list))
    line_num += 1.0
    
    for file in directory_list:
        text = str(file)
        text_file_list.insert(str(line_num), "%s\n" %file)
        line_num += 1.0
    
    # Change status to disabled to prevent accidental user edits
    text_file_list.config(state="disabled")

    # Repeat every cycle
    window.after(CYCLE_TIME, print_file_preview)


def load_and_parsepdf(pdf: str) -> dict:
    """Return a dict containing invoice date parts and invoice number.

    """
    # Create full file path for passed pdf
    pdf_path = os.path.join(source_path, current_file)
    current_pdf = pdfquery.PDFQuery(pdf_path)
    update_console("Loading file: %s" %pdf)
    
    # Open pdf
    current_pdf.load()
    
    # Set up a new dictionary for parsed elements
    parsed_elements: dict = {}

    # Get date from invoice and save parts into list [YYYY, MM, DD]
    date_string = current_pdf.pq(\
        'LTTextLineHorizontal:overlaps_bbox("%d, %d, %d, %d")' \
            % (invoice_date[0], invoice_date[1], invoice_date[2], invoice_date[3])).text()
    
    # Use regular expression to find year, month, day
    date_string = re.findall('\\d+', date_string)
    update_console("Date is: %d/%d/%d" % (int(date_string[2]), int(date_string[0]), int(date_string[1])))
    parsed_elements["inv_date"] = date_string
    
    # Get invoice number
    number_string = current_pdf.pq(\
        'LTTextLineHorizontal:overlaps_bbox("%d, %d, %d, %d")' \
            % (invoice_number[0], invoice_number[1], invoice_number[2], invoice_number[3])).text()
    
    # Use regular expression to find invoice number
    numbers = re.findall('\\d+', number_string)
    update_console("Invoice number is: %s" %numbers[0])
    parsed_elements["inv_number"] = numbers[0]

    # Close pdf
    update_console("Closing file: %s" %pdf)
    current_pdf.file.close()

    return parsed_elements


def is_pdf(file: str) -> bool:
    """Returns true if file ends with '.pdf' and false if any other ending is found.
    
    """
    if file.endswith(".pdf"):
        return True
    else:
        return False


def update_progress():
    """Updates current progress of scanned pdf files within source directory. Only accounts for
    'pdf' format files.
    
    """
    global progress_percentage
    if file_count == 0:
        pass
    else:
        progress_percentage = int(file_scan_count / file_count) * 100
    

def update_console(text: str):
    """Updates console text box with provided string by inserting at top and pushing past messages
    down.
    
    """
    # Change status to normal for editing
    text_console.config(state="normal")
    # Append to console
    text_console.insert("1.0", text + "\n")
    # Change status to disabled to prevent editing
    text_console.config(state="disabled")


def on_run():
    """Starts when "Run Parser" button is clicked. Acts as the main working loop for parsing
    files. Ends when directory_list == 0.
    
    """
    global current_file
    global last_copied_file
    global directory_list
    global current_file_ext_path
    global current_file_ext_destination_path
    global file_num
    global file_scan_count

    # Recursively work through full file list
    if len(directory_list) > 0:
        current_file = directory_list[0]
        update_console("Currently working on file: %s" %current_file)

        # Check if it is a pdf - remove from files list if not
        if not is_pdf(current_file):
            update_console("Skipping to next file (%s) is not a valid pdf..." %current_file)
            directory_list.remove(current_file)
            current_file = directory_list[0]
        
        # Load and parse the current pdf
        parsed_elements = load_and_parsepdf(current_file)

        # Copy file to destination directory
        update_console("Attempting to copy: '%s'" %current_file)
        try:
            current_file_ext_path = os.path.join(source_path, current_file)
            shutil.copy(current_file_ext_path, destination_path)
            current_file_ext_destination_path = os.path.join(destination_path, current_file)
            update_console("Copy successful.")
        except shutil.SameFileError as e:
            update_console("ERROR: " + str(e))

        # Rename the freshly copied file using parsed elements
        date_part = str(parsed_elements["inv_date"][2] + parsed_elements["inv_date"][0] + parsed_elements["inv_date"][1])
        new_file_base_name = date_part + '_' + parsed_elements["inv_number"]
        new_file_fullname = new_file_base_name + ".pdf"
        
        # Get new full path for new file added to destination folder
        new_file_name_ext_path = os.path.join(destination_path, new_file_fullname)
        update_console("Attempting to modify name to: %s" %new_file_fullname)

        # Check if filepath exists and append identifier, if needed
        if os.path.exists(new_file_name_ext_path):
            update_console("Filename already exists - appending new tag...")
            new_file_base_name += "-(%d)" %file_num
            new_file_fullname = new_file_base_name + ".pdf"
            new_file_name_ext_path = os.path.join(destination_path, new_file_fullname)
            file_num =+ 1
            update_console("Name given to file is: %s" %new_file_fullname)
        os.rename(current_file_ext_destination_path, new_file_name_ext_path)

        # Get next file in list
        directory_list.remove(current_file)
        file_scan_count += 1
        if len(directory_list) > 0:
            current_file = directory_list[0]
        
        # Recursively call to move through list
        window.after(500, on_run)
    else:
        update_console("No more files found in directory left to scan.")


# --- GUI ---
# Tkinter window
window = tk.Tk(className=APP_NAME)
window.resizable(width=False, height=False)

frame_title = tk.Frame(
    master=window,
    width=800,
    bg="#F4E8DD",
    border=10
)

label_main = tk.Label(
    master=frame_title,
    text=APP_NAME.upper(),
    bg="#F4E8DD",
    fg="black"
)

frame_title.pack(fill=tk.BOTH)
label_main.pack()

# Frame - directory paths
frame_directories = tk.Frame(
    master=window,
    bg="#7BAFD4",
    borderwidth=10
)
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

# Source button
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

# Destination button
button_dest_directory = tk.Button(
    master=frame_directories,
    text= "Select Destination Directory",
    height= 2,
    width= 30,
    border=5,
    command=set_dest_path
)
button_dest_directory.pack()
label_dest_directory.pack()

# File list in text box
frame_files=tk.Frame(
    width=100,
    height=100,
    bg="#7BAFD4",
    border=10
)
frame_files.pack(fill=tk.BOTH)

label_file_list = tk.Label(
    master=frame_files,
    text="File List",
    bg="#7BAFD4"
)
label_file_list.pack(side=tk.LEFT)

text_file_list = tk.Text(
    master=frame_files,
    width=70, height=20,
    bg="#13294B",
    fg="white",
    border=3
)
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

# invoice type buttons
frame_progress = tk.Frame(
    master=window,
    bg="#7BAFD4",
    border=10
)
frame_progress.pack(fill=tk.BOTH)

label_progress = tk.Label(
    master=frame_progress,
    text="%d%% complete --- %d out of %d files scanned" %(progress_percentage, file_scan_count, len(directory_list)),
    bg="#7BAFD4",
    fg="yellow"
)
label_progress.pack()

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

update_progress_label()
print_file_preview()
window.mainloop()
