from zipfile import ZipFile
import shutil
# from PIL import Image
import PIL.Image
import PIL.ImageOps
import os, getpass
import tkinter as tk
from tkinter import *
from tkinter import filedialog
from tkinter import messagebox
import tkinter.ttk as ttk
from tkinter import font as tkFont

class SampleApp(tk.Tk):

    def __init__(self):
        tk.Tk.__init__(self)

        self.files = []
        #self.destFile = ""
        self.script = ""
        self.destFlag = False
        self.formats = ('.jpg', '.jpeg')
        self.quality = 25

        container = tk.Frame(self)
        container.pack(side="top", fill="both", expand=True)
        container.grid_rowconfigure(0, weight=1)
        container.grid_columnconfigure(0, weight=1)
        container.tk_setPalette(background='#e6e6e6')
        container.winfo_toplevel().title("Denteon Zip")

        self.frames = {}
        for F in (FileSelectionPage, OtherPage):
            page_name = F.__name__
            frame = F(parent=container, controller=self)
            self.frames[page_name] = frame

            frame.grid(row=0, column=0, sticky="nsew")

        self.show_frame("FileSelectionPage")

    def get_page(self, page_name):
        return self.frames[page_name]
    
    # Raise specified frame and reset geometry
    def show_frame(self, page_name):
        '''Show a frame for the given page name'''
        for frame in self.frames.values():
            frame.grid_remove()
        frame = self.frames[page_name]
        frame.grid()
        frame.tkraise()
        frame.winfo_toplevel().geometry("")
        frame.update_idletasks()
        x = (frame.winfo_screenwidth() - frame.winfo_reqwidth()) / 2
        y = (frame.winfo_screenheight() - frame.winfo_reqheight()) / 3
        self.geometry("+{}+{}".format(int(x), int(y)))

class FileSelectionPage(tk.Frame):
    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)
        self.controller = controller

        def fileHandler():
            fileSize = 0
            fileList = [[]]
            oversizedFiles = []
            progress = 0
            destination = destination_var.get().replace("\\", "/")
            compression_quality = quality_var.get()
            outputName = outputNamingVar.get()
            quality = int(compression_quality)

            # Error handling
            if not self.controller.files:
                messagebox.showwarning(title="No Files Selected", message="No files selected! Please select file(s) or folder and then select compress and zip.")
                return
            if (destination == '' or not os.path.isdir(destination)):
                messagebox.showwarning(title="Invalid Destination Directory", message="Select a valid destination directory to continue.")
                return
            if quality < 0 or quality > 100:
                messagebox.showwarning(title="Incorrect Quality Setting", message="Quality must be set between 0 to 100. Default is 25.")
                return
            if (outputName == ''):
                messagebox.showwarning(title="Missing Output Name", message="Please provide an output name.")
                return
            print("Output folder = " + destination)
            print("Compression Quality = " + str(compression_quality))

            # Compress files
            filesToBeZipped = compressFiles(destination, compression_quality, outputName)

            # Start zipping progress bar and label
            zip_label = ttk.Label(self, text="Files being zipped")
            zip_label.grid(row=4,column=3,sticky= "nsew")
            progress_bar.start()
            progressStep = float(100.0/len(filesToBeZipped))

            count = 0
            outerCount = 0
            # Zipping logic loop
            for item in filesToBeZipped:
                # progress bar step up
                progress += progressStep
                progressVar.set(progress)
                progress_bar.update_idletasks()
                itemSize = os.path.getsize(item)
                # Check if compressed file is less than 25mb(26,214,000 bytes)
                if itemSize > 26000000:
                        print(item + " is too large!")
                        oversizedFiles.append(item)
                        continue
                fileSize = fileSize + itemSize
                print("filesize = " + str(fileSize) + " file = " + item)
                # Max zip file of 25mb
                if fileSize > 25000000:
                    outerCount+=1
                    fileSize = itemSize
                    fileList.append([])
                fileList[outerCount].append(item)

            # Zip files
            for i in range(len(fileList)):
                with ZipFile(destination + '/' + outputName + ' (' + str(i) + ').zip','w') as zip:
                        # writing each file one by one
                        for file in fileList[i]:
                            zip.write(file, os.path.basename(file))

            progressVar.set(0)
            progress_bar.stop()
            progress_bar.update_idletasks()
            zip_label.destroy()

            # Completion popup messages
            if oversizedFiles:
                messagebox.showwarning(title="Oversized files", message="The following files where too large to zip: " + str(oversizedFiles))
            else:
                messagebox.showinfo(title="Complete", message="Images successfully compressed and zipped!")

            clearFiles()
            print("Compression and zipping Complete!")
            return

        def compressFiles(destination, qual, fileName):
            compressedFiles = []
            count = 0
            progress = 0
            compress_label = ttk.Label(self, text="Files being compressed")
            compress_label.grid(row=4,column=3,sticky= "nsew")
            progressStep = float(100.0/len(self.controller.files))

            # compress jpeg files, skip all other formats
            for img in self.controller.files:
                progress += progressStep
                progressVar.set(progress)
                progress_bar.update_idletasks()
                if os.path.splitext(img)[1].lower() in self.controller.formats:
                    print('compressing', img)
                    image = PIL.Image.open(img)
                    # Preserves images original rotation
                    picture = PIL.ImageOps.exif_transpose(image)
                    path = destination + '/' + fileName + ' (' + str(count) + ').jpg'
                    picture.save(path, "JPEG", optimize = True, quality = qual)
                    compressedFiles.append(path)
                    count = count + 1
                else:
                    #TODO: Find better way to handle other file types (ex. mov)
                    print('skipping ', img)
                    path = destination + '/' + fileName + ' (' + str(count) + ')' + os.path.splitext(img)[1].lower()
                    compressedFiles.append(path)
                    shutil.copy(img, path)
                    count = count + 1
            progressVar.set(100)
            progress_bar.update_idletasks()
            compress_label.destroy()
            return compressedFiles 

        def selectFiles():
            user = getpass.getuser()
            filelist = tk.filedialog.askopenfilename(initialdir='C:/Users/%s' %user, multiple=True)
            for filename in filelist:
                if filename not in self.controller.files:
                    try:
                        selected_list.insert('end', (filename))
                        self.controller.files.append(filename)
                    except:
                        print("could not add: " + filename)

        def selectFolders():
            user = getpass.getuser().lower()
            folder = filedialog.askdirectory(initialdir='C:/Users/%s' %user)
            if (folder == ''):
                return
            addFolder(folder)

        def addFolder(folder):
            try:
                filelist = os.scandir(folder)
            except:
                messagebox.showwarning("Access Denied", "Can't Access " + folder)
                return
            for filename in filelist:
                absolute_filename = folder + '/' + filename.name
                if os.path.isfile(absolute_filename):
                    if absolute_filename not in self.controller.files:
                        try:
                            selected_list.insert('end', absolute_filename)
                            self.controller.files.append(absolute_filename)
                        except:
                            print("could not add: " + absolute_filename)
                elif os.path.isdir(absolute_filename):
                    # TODO: Do I want this to be recursive, optional with selector?
                    # addFolder(absolute_filename)
                    continue

        def removeFile():
            selected = selected_list.curselection()
            try:
                value = selected_list.get(selected[0])
            except:
                print("No file is selected")
                return
            try:
                selected_list.delete(selected[0])
                self.controller.files.remove(value)
            except:
                print("Error removing file from files list")

        def clearFiles():
            self.controller.files.clear()
            try:
                selected_list.delete(0,'end')
            except:
                print("Error removing file from files list")

        def selectDestination():
            user = getpass.getuser().lower()
            folder = filedialog.askdirectory(initialdir='C:/Users/' + user)
            if (folder == ''):
                return
            destination_var.set(folder)

        # Fonts
        helv36 = tkFont.Font(family='Helvetica', size=18, weight='bold')

        # Variables
        quality_var = IntVar(self, value="25")
        progressVar = DoubleVar()
        destination_var = StringVar(self, value="")
        outputNamingVar = StringVar(self, value="compressedImages")

        # Frames
        manage_frame = ttk.Frame(self, borderwidth=5, relief="ridge")
        entry_frame = ttk.Frame(self, borderwidth=5, relief="ridge")

        # Listbox
        selected_list = tk.Listbox(self, bg='#ffffff', width = 100, height = 30)
        
        # Buttons
        file_button = ttk.Button(manage_frame, text="Select File(s)", command=lambda: selectFiles())
        folder_button = ttk.Button(manage_frame, text="Select Folder", command=lambda: selectFolders())
        remove_button = ttk.Button(manage_frame, text="Remove Selected", command=lambda: removeFile())
        clear_button = ttk.Button(manage_frame, text="Clear List", command=lambda: clearFiles())
        destination_button = ttk.Button(entry_frame, text="select", command=lambda: selectDestination())
        process_button = tk.Button(self, text="compress and zip", command=lambda: fileHandler(), font=helv36)

        # Entry
        destination_entry = tk.Entry(entry_frame, textvariable=destination_var)
        quality_entry = tk.Entry(entry_frame, textvariable=quality_var, justify="center")
        output_naming_entry = tk.Entry(entry_frame, textvariable=outputNamingVar, justify="center")

        # Labels
        selected_label = ttk.Label(self, text="Selected files:")
        manage_label = ttk.Label(self, text="Manage files:")
        destination_label = ttk.Label(entry_frame, text="Destination:")
        quality_label = ttk.Label(entry_frame, text="Quality (0-100):")
        output_naming_label = ttk.Label(entry_frame, text="Output name:")

        # Progress bar
        progress_bar = ttk.Progressbar(self, orient="horizontal", variable=progressVar, mode="determinate", maximum=100, value=0)

        # Grid layout
        self.grid(padx=5, pady=(2,0))

        selected_label.grid(row=0, column=0, sticky="w")
        selected_list.grid(row=1, column=0, rowspan=3, columnspan=3, sticky="nsew")
        manage_label.grid(row=0, column=3, pady=0)

        manage_frame.grid(row=1, column=3, pady=0, sticky="new")
        file_button.grid(row=0, column=0, padx=0, pady=5, sticky="ew")
        folder_button.grid(row=1, column=0, padx=0, pady=5, sticky="ew")
        remove_button.grid(row=2, column=0, padx=0, pady=(5,5), sticky="ew")
        clear_button.grid(row=3, column=0, padx=0, pady=5, sticky="ew")

        entry_frame.grid(row=2, column=3, pady=0, sticky="new")
        destination_label.grid(row=0, column=0, padx=0, pady=0, sticky="w")
        destination_entry.grid(row=1, column=0, padx=0, pady=0, columnspan=2, sticky="ew")
        destination_button.grid(row=2, column=0, padx=0, pady=0, sticky="w")
        output_naming_label.grid(row=3, column=0, padx=0, pady=0, sticky="w")
        output_naming_entry.grid(row=3, column=1, padx=0, pady=0, sticky="w")
        quality_label.grid(row=4, column=0, padx=0, pady=(30,0), sticky="w")
        quality_entry.grid(row=4, column=1, padx=0, pady=(30,0))

        process_button.grid(row=3, column=3, pady=(10,0))

        progress_bar.grid(row=4, column=0, columnspan=3, pady=5, sticky="ew")

        # configure
        self.columnconfigure(0, weight=2)
        self.rowconfigure(1, weight=1)
        self.rowconfigure(2, weight=1)
        self.columnconfigure(3, weight=1)
        self.rowconfigure(3, weight=1)
        manage_frame.columnconfigure(0, weight=1)
        manage_frame.rowconfigure(0, weight=1)
        entry_frame.columnconfigure(1, weight=1)
        entry_frame.rowconfigure(0, weight=1)

#TODO: remove or add to project
class OtherPage(tk.Frame):
    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent, width=450, height=50, pady=3)
        self.controller = controller

if __name__ == "__main__":
    app = SampleApp()
    app.mainloop()
