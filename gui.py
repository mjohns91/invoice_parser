# gui.py

import tkinter as tk
import os
import shutil
import parser

from tkinter import filedialog

__author__ = "M. Johnson"
__version__ = "1.0"

CYCLE_TIME: int = 100
APP_NAME = "invoice parser v1.0"
COLORS = {
        "CarolinaBlue":"#7BAFD4",
        "Navy":"#13294B",
        "Black":"#151515",
        "White":"#FFFFFF",
        "Gray":"#F8F8F8",
        "BasinSlate":"#4F758B",
        "LongleafPine":"#00594C"
    }


class GUI(tk.Frame):
    """Acts as the main graphical user interface for the application"""

    def __init__(self, parent, *args, **kwargs):
        tk.Frame.__init__(self, parent, *args, **kwargs)
        
        self.parent = parent
        self.source_path: str = "<no source path currently set>"
        self.destination_path: str = "<no destination path currently set>"
        self.file_count: int = 0
        self.scanned_count: int = 0
        self.progress_percent: int = 0
        self.directory_list: list = []
        self.current_file: str = "<no current file currently selected>"
        self.last_copied_file: str = "<no previous file copied>"
        self.file_num: int = 0
        self.current_file_ext_path: str = "<no current file ext path set>"
        self.current_file_ext_destination_path: str = "<no destination path set>"
        self.parsed_data: dict = {}
        
        root.resizable(width=False, height=False)

        # Header
        self.frame_header = tk.Frame(
            master=self,
            width=800,
            bg=COLORS["CarolinaBlue"],
            border=10
        )

        self.label_main = tk.Label(
            master=self.frame_header,
            text=APP_NAME.upper(),
            bg=COLORS["Gray"],
            fg="black"
        )

        # Directory Paths
        self.frame_directories = tk.Frame(
            master=self,
            bg=COLORS["CarolinaBlue"],
            borderwidth=10
        )

        self.label_source_directory = tk.Label(
            master=self.frame_directories,
            text="Source directory path: %s" %self.source_path,
            anchor="w",
            justify="left",
            borderwidth=5,
            border=5,
            bg=COLORS["CarolinaBlue"]
        )

        self.label_dest_directory = tk.Label(
            master=self.frame_directories,
            text="Destination directory path: %s" %self.destination_path,
            anchor="w",
            justify="left",
            borderwidth=5,
            border=5,
            bg=COLORS["CarolinaBlue"]
        )

        # Source button
        self.button_src_directory = tk.Button(
            master=self.frame_directories,
            text= "Select Source Directory",
            height= 2,
            width= 30,
            border=5,
            command=self.set_source_path
        )

        # Destination button
        self.button_dest_directory = tk.Button(
            master=self.frame_directories,
            text="Select Destination Directory",
            height=2,
            width=30,
            border=5,
            command=self.set_dest_path
        )

        # File list in text box
        self.frame_files=tk.Frame(
            master=self,
            width=100,
            height=100,
            bg=COLORS["CarolinaBlue"],
            border=10
        )

        self.label_file_list = tk.Label(
            master=self.frame_files,
            text="File List",
            bg=COLORS["CarolinaBlue"]
        )
        

        self.text_file_list = tk.Text(
            master=self.frame_files,
            width=70, height=20,
            bg=COLORS["Navy"],
            fg="white",
            border=3
        )
        
        self.label_console = tk.Label(
            master=self.frame_files,
            text="Console Output",
            bg=COLORS["CarolinaBlue"]
        )
        
        self.text_console = tk.Text(
            master=self.frame_files,
            height=20,
            width=100,
            bg=COLORS["Navy"],
            fg="white",
            state="disabled",
            border=3
        )
        
        # invoice type buttons
        self.frame_progress = tk.Frame(
            master=self.parent,
            bg=COLORS["CarolinaBlue"],
            border=10
        )
        
        self.label_progress = tk.Label(
            master=self.frame_progress,
            text="%d%% complete | %d out of %d files scanned" %(self.progress_percent, self.scanned_count, len(self.directory_list)),
            bg=COLORS["CarolinaBlue"],
            fg="yellow"
        )
        
        # run button
        self.frame_run_control = tk.Frame(
            master=self.parent,
            border=10
        )
        
        self.button_run = tk.Button(
            master=self.frame_run_control,
            text="Run Parser",
            bg=COLORS["LongleafPine"],
            fg="white",
            command=self.on_run
        )
        
        # Packing components
        self.frame_header.pack(fill=tk.BOTH)
        self.label_main.pack()
        
        self.frame_directories.pack(fill=tk.BOTH)
        self.button_src_directory.pack()
        self.label_source_directory.pack()
        self.button_dest_directory.pack()
        self.label_dest_directory.pack()

        self.frame_files.pack(fill=tk.BOTH)
        self.label_file_list.pack(side=tk.LEFT)
        self.text_file_list.pack(side=tk.LEFT)
        self.label_console.pack(side=tk.RIGHT)
        self.text_console.pack(side=tk.RIGHT)

        self.frame_progress.pack(fill=tk.BOTH)
        self.label_progress.pack()

        self.frame_run_control.pack()
        self.button_run.pack()


    def set_source_path(self):
        self.source_path = filedialog.askdirectory()
        self.label_source_directory.config(text="Selected source path: %s" %self.source_path)
        self.update_console("Source path > %s" %self.source_path)
        self.scan_src_directory()
        self.print_file_preview()
        self.update_progress_label()


    def set_dest_path(self):
        self.destination_path = filedialog.askdirectory()
        self.label_dest_directory.config(text="Selected destination path: %s" %self.destination_path)
        self.update_console("Destination path > %s" %self.destination_path)


    def scan_src_directory(self):
        """Scans current directory set as source_path var and updates global directory_list var with a list
        of all files found in path. This is set via tkinter button.
        
        """
        self.directory_list = os.listdir(path=self.source_path)
        self.file_count = len(self.directory_list)
    

    def update_progress_label(self):
        """Updates the GUI's progress label on a repeating cycle.
    
        """
        self.calculate_progress()
        self.label_progress.config(text="%d%% complete | %d out of %d files scanned" %(self.progress_percent, self.scanned_count, self.file_count))
        root.after(CYCLE_TIME, self.update_progress_label)


    def calculate_progress(self):
        """Updates current progress of scanned pdf files within source directory. Only accounts for
        'pdf' format files.
        
        """
        if self.file_count == 0:
            pass
        else:
            self.progress_percent = int(self.scanned_count / self.file_count) * 100


    def update_console(self, text: str):
        """Updates console text box with provided string by inserting at top and pushing past messages
        down.
        
        """
        # Change status to normal for editing
        self.text_console.config(state="normal")
        # Append to console
        self.text_console.insert("1.0", text + "\n")
        # Change status to disabled to prevent editing
        self.text_console.config(state="disabled")


    def print_file_preview(self):
        """Update the GUI file preview text box. Clears the text box and prints remaining files
        in directory list.

        """
        # Change status to normal for editing
        self.text_file_list.config(state="normal")

        # Clear the text box
        self.text_file_list.delete("1.0", tk.END)
        line_num = 1.0
        
        self.text_file_list.insert(str(line_num), "%d file(s) found in directory:\n" %len(self.directory_list))
        line_num += 1.0
        
        for file in self.directory_list:
            self.text_file_list.insert(str(line_num), "%s\n" %file)
            line_num += 1.0
        
        # Change status to disabled to prevent accidental user edits
        self.text_file_list.config(state="disabled")

        # Repeat every cycle
        root.after(CYCLE_TIME, self.print_file_preview)

    def on_run(self):
        """Starts when "Run Parser" button is clicked. Acts as the main working loop for parsing
        files. Ends when directory_list == 0.
        
        """
        # Recursively work through full file list
        if len(self.directory_list) > 0:
            self.current_file = self.directory_list[0]
            self.update_console("Currently working on file: %s" %self.current_file)

            # Check if it is a pdf - remove from files list if not
            if not parser.is_pdf(self.current_file):
                self.update_console("Skipping to next file (%s) is not a valid pdf..." %self.current_file)
                self.directory_list.remove(self.current_file)
                self.current_file = self.directory_list[0]
            
            # Load and parse the current pdf
            self.parsed_data = parser.load_and_parse_pdf(self.source_path, self.current_file, self.parsed_data)

            # Copy file to destination directory
            self.update_console("Attempting to copy: '%s'" %self.current_file)
            try:
                self.current_file_ext_path = os.path.join(self.source_path, self.current_file)
                shutil.copy(self.current_file_ext_path, self.destination_path)
                self.current_file_ext_destination_path = os.path.join(self.destination_path, self.current_file)
                self.update_console("Copy successful.")
            except shutil.SameFileError as e:
                self.update_console("ERROR: " + str(e))

            # Rename the freshly copied file using parsed elements
            date_part = str(self.parsed_data["inv_date"][2] + self.parsed_data["inv_date"][0] + self.parsed_data["inv_date"][1])
            new_file_base_name = date_part + '_' + self.parsed_data["inv_number"]
            new_file_fullname = new_file_base_name + ".pdf"
            
            # Get new full path for new file added to destination folder
            new_file_name_ext_path = os.path.join(self.destination_path, new_file_fullname)
            self.update_console("Attempting to modify name to: %s" %new_file_fullname)

            # Check if filepath exists and append identifier, if needed
            if os.path.exists(new_file_name_ext_path):
                self.update_console("Filename already exists - appending new tag...")
                new_file_base_name += "-(%d)" %self.file_num
                new_file_fullname = new_file_base_name + ".pdf"
                new_file_name_ext_path = os.path.join(self.destination_path, new_file_fullname)
                self.file_num =+ 1
                self.update_console("Name given to file is: %s" %new_file_fullname)
            os.rename(self.current_file_ext_destination_path, new_file_name_ext_path)

            # Get next file in list
            self.directory_list.remove(self.current_file)
            self.scanned_count += 1
            if len(self.directory_list) > 0:
                self.current_file = self.directory_list[0]
            
            # Recursively call to move through list
            root.after(500, self.on_run)
        else:
            self.update_console("No more files found in directory left to scan.")

if __name__ == "__main__":
    root = tk.Tk(className=APP_NAME)
    GUI(root).pack(side="top", fill="both", expand=True)
    root.mainloop()
