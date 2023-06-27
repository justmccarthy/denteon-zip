from zipfile import ZipFile
import shutil
# from PIL import Image
import PIL.Image
import os, getpass
import tkinter as tk
from tkinter import *
from tkinter import filedialog
from tkinter import messagebox
import tkinter.ttk as ttk

class SampleApp(tk.Tk):

    def __init__(self):
        tk.Tk.__init__(self)

        self.files = []
        self.destFile = ""
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
        for F in (FileSelectionPage, CodePage):
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

# Frame for selecting files to be sorted
class FileSelectionPage(tk.Frame):

    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)
        self.controller = controller

        f1 = tk.Frame(self)
        f2 = tk.Frame(self)
        f3 = tk.Frame(self)

        self.grid_rowconfigure(0, weight=0)
        self.grid_rowconfigure(1, weight=1)
        self.grid_rowconfigure(2, weight=0)
        
        self.grid_columnconfigure(0, weight=0)
        self.grid_columnconfigure(1, weight=1)
        self.grid_columnconfigure(2, weight=0)

        f3.grid_rowconfigure(0, weight=1)

        f3.grid_columnconfigure(0, weight=1)


        label = tk.Label(self, text="Select files to be sorted")
        label.grid(row=0, column=1, sticky = "s")

        # Add multiselected delete: add back (selectmode="multiple",)
        self.selected_list = tk.Listbox(f3, bg='#ffffff', width = 100, height = 30)
        self.selected_list.grid(row = 0, column = 0, sticky= "nsew")

        file_button = tk.Button(f1, text="Select File(s)",
                                command=self.addFiles)
        file_button.grid(row=0, column=0, pady = 10)

        file_button = tk.Button(f1, text="Select Folder",
                                command=self.addFolders)
        file_button.grid(row=1, column=0, pady = 10)

        # TODO: Add extra input fields, figure out how to display values
        #       and event handler for updating values
        # quality_label = tk.Label(self, text="quality 0 - 100")
        # quality_label.grid(row=2, column=0, pady = 10)
        # quality_entry = tk.Entry(f1, textvariable=self.controller.quality)
        # quality_entry.grid(row=2, column=0, pady = 10)

        file_button = tk.Button(f2, text="Remove Selected",
                                command=self.removeFile)
        file_button.grid(row=0, column=0, pady = 10)

        file_button = tk.Button(f2, text="Clear List",
                                command=self.clearFiles)
        file_button.grid(row=1, column=0, pady = 10)

        progressBar = ttk.Progressbar(self, orient="horizontal", mode="determinate", maximum=100, value=0)

        # TODO: update redirect button
        # next_button = tk.Button(self, text="Next",
        #                         command=lambda: controller.show_frame("CodePage"))
        # next_button.grid(row=2, column=1, pady = 10)

        next_button = tk.Button(self, text="compress and zip",
                                command=self.fileHandler)
        next_button.grid(row=2, column=1, pady = 10)

        f1.grid(row=1, column=0, padx = 10)
        f2.grid(row=1, column=2, padx = 10, sticky = "e")
        f3.grid(row=1, column=1, sticky = "nsew")

        #label = tk.Label(self, text="")
        #label.pack

    def fileHandler(self):
        fileSize = 0
        fileList = [[]]
        self.controller.destFile = ''
        oversizedFiles = []
        progress = 0
        progressVar = DoubleVar()
        
        # Get destination folder
        user = getpass.getuser().lower()
        self.controller.destFile = filedialog.askdirectory(initialdir='C:/Users/' + user)

        # Error handling
        if not self.controller.files:
            messagebox.showwarning(title="No files selected", message="No files selected! Please select file(s) or folder and then select compress and zip")
            return
        if (self.controller.destFile == ''):
            # messagebox.showwarning(title="File selection error", message="Select a destination file for compressed images and zip files.")
            return
        print("Output folder = " + self.controller.destFile)

        filesToBeZipped = compressFiles(self)
        
        popup = Toplevel()
        Label(popup, text="Files being zipped").grid(row=0,column=0,sticky= "nsew")
        progressBar = ttk.Progressbar(popup, orient="horizontal", variable=progressVar, mode="determinate", maximum=100, value=0)
        progressBar.grid(row=1, column=0)
        popup.pack_slaves()
        progressBar.start()
        
        count = 0
        outerCount = 0
        progressStep = float(100.0/len(filesToBeZipped))
        for item in filesToBeZipped:
            popup.update()
            progress += progressStep
            progressVar.set(progress)
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

        for i in range(len(fileList)):
            with ZipFile(self.controller.destFile + '/compressedImagesTest_' + str(i) + '.zip','w') as zip:
                    # writing each file one by one
                    for file in fileList[i]:
                        zip.write(file, os.path.basename(file))

        # Completion messages
        progressBar.stop()
        popup.destroy()
        if oversizedFiles:
            messagebox.showwarning(title="Oversized files", message="The following files where too large to zip: " + str(oversizedFiles))
        else:
            messagebox.showinfo(title="Complete", message="Images successfully compressed and zipped!")

        self.clearFiles()
        print("Compression and zipping Complete!")
        return

    # Select individual files to be sorted
    def addFiles(self):
        print(self.controller.quality)
        user = getpass.getuser()
        filelist = tk.filedialog.askopenfilename(initialdir='C:/Users/%s' % user, multiple=True)
        for filename in filelist:
            if filename not in self.controller.files:
                try:
                    self.selected_list.insert('end', (filename))
                    self.controller.files.append(filename)
                except:
                    print("could not add: " + filename)

    # Select folders to be sorted
    def addFolders(self):
        user = getpass.getuser().lower()
        folder = filedialog.askdirectory(initialdir='C:/Users/' + user)
        if (folder == ''):
            return
        # confirm = messagebox.askyesno('Confirm', 'Are you sure you want to sort from: ' + folder + '?')
        # if not confirm:
        #     return
        self.addFolder(folder)

    # add folder to list calls self recursively for sub folders
    def addFolder(self, folder):
        try:
            filelist = os.scandir(folder)
        except:
            messagebox.showwarning("Access Denied", "Can't Access " + folder)
            return
        for filename in filelist:
            if os.path.isfile(folder + '/' + filename.name):
                if filename not in self.controller.files:
                    try:
                        self.selected_list.insert('end', (folder + '/' + filename.name))
                        self.controller.files.append(folder + '/' + filename.name)
                    except:
                        print("could not add: " + folder + '/' + filename.name)
            elif os.path.isdir(folder + '/' + filename.name):
                self.addFolder(folder + '/' + filename.name)

    # Remove selected files
    def removeFile(self):
        selected = self.selected_list.curselection()
        try:
            value = self.selected_list.get(selected[0])
        except:
            print("No file is selected")
            return
        try:
            self.selected_list.delete(selected[0])
            self.controller.files.remove(value)
        except:
            print("Error removing file from files list")

    def clearFiles(self):
        self.controller.files.clear()
        try:
            self.selected_list.delete(0,'end')
        except:
            print("Error removing file from files list")

    
class CodePage(tk.Frame):
    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent, width=450, height=50, pady=3)
        self.controller = controller

# Compress files, returning array of files
def compressFiles(self):
    compressedFiles = []
    count = 0

    progress = 0
    progressVar = DoubleVar()
    popup = Toplevel()
    Label(popup, text="Files being compressed").grid(row=0,column=0,sticky= "nsew")
    progressBar = ttk.Progressbar(popup, orient="horizontal", variable=progressVar, mode="determinate", maximum=100, value=0)
    progressBar.grid(row=1, column=0)
    popup.pack_slaves()
    progressBar.start()
    progressStep = float(100.0/len(self.controller.files))
    for img in self.controller.files:
        popup.update()
        progress += progressStep
        progressVar.set(progress)
        if os.path.splitext(img)[1].lower() in self.controller.formats:
            print('compressing', img)
            picture = PIL.Image.open(img)
            path = self.controller.destFile + "/Compressed_"+ str(count) + ".jpg"
            picture.save(path, 
                "JPEG", 
                optimize = True, 
                quality = 25)
            compressedFiles.append(path)
            count = count + 1
        else:
            #TODO: Find better way to handle other file types (ex. mov)
            print('skipping ', img)
            path = self.controller.destFile + "/Compressed_"+ str(count) + os.path.splitext(img)[1].lower()
            compressedFiles.append(path)
            shutil.copy(img, path)
            count = count + 1
    progressVar.set(100)
    progressBar.stop()
    popup.destroy()
    return compressedFiles 

#TODO: helper functions DELETE
def printfiles(self):
    for img in self.controller.files:
        print(img)


if __name__ == "__main__":
    app = SampleApp()
    app.mainloop()
