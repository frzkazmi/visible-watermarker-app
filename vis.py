import Tkinter as Tk
import tkFileDialog
import os, sys, time
from PIL import Image, ImageDraw, ImageFont, ImageTk


class MyApp:
    """Begin a Tkinter-based application"""
    
    def __init__(self, root):
        """initializer for Tkinter-based application"""
        self.root=root
        self.root.title("Visible Wtermarker")
        NoticeFrame = Tk.Frame(self.root)
        NoticeFrame.pack()
        headertext = u"""
        Created By:
		MOHD JOUN 
		NITIN KATIYAR
        """
        Tk.Label(NoticeFrame,text=headertext).pack()
        ButtonFrame = Tk.Frame(self.root)
        ButtonFrame.pack()       
        SelButton = Tk.Button(ButtonFrame, 
            text="Select Directory", command=self.select)
        SelButton.pack(side="left")
        QuitButton = Tk.Button(ButtonFrame, text="Quit", 
            command=self.quit)
        QuitButton.pack(side="left")

        OptionsFrame = Tk.Frame(self.root)
        OptionsFrame.pack()
        self.EXIFvar = Tk.IntVar()
        self.EXIFCheckbox = Tk.Checkbutton(
            OptionsFrame,
            text="Preserve EXIF (requires JHead)",
            variable = self.EXIFvar)
        self.EXIFCheckbox.pack(side="top")
        self.Progressvar = Tk.IntVar()
        self.ProgressCheckbox = Tk.Checkbutton(
            OptionsFrame,
            text="Show progress",
            variable = self.Progressvar)
        self.ProgressCheckbox.pack(side="left")
               
        self.StatusFrame = Tk.Frame(self.root)
        self.StatusFrame.pack()
        self.ImageLabel = Tk.Label(self.StatusFrame)
        self.ImageLabel.pack()
        self.FilenameLabel = Tk.Label(self.StatusFrame)
        self.FilenameLabel.pack()

    def select(self):
        dirname = tkFileDialog.askdirectory()
        if dirname != '':
            os.path.walk(dirname, self.process_files, None)
            print "PROCESSING COMPLETED.  SELECT MORE FILES OR QUIT."
        else:
            print "NO DIRECTORY SELECTED."
        return
    
    def quit(self):
        print "EXITING."
        sys.exit()

    def process_files(self, junk, dirpath, namelist):
        for filename in namelist:
            stamped_filename = self.getstampedfilename(filename)
            if stamped_filename is not None:
                if os.path.isfile(os.path.join(dirpath,stamped_filename)):
                    print "FILE EXISTS, SKIPPING:", stamped_filename
                else:
                    self.updatestatus(dirpath, filename)
                    datetext = self.timestamp(dirpath, filename, 
                        stamped_filename)
                    print "FILE IMPRINTED:", stamped_filename, datetext
                    
    def updatestatus(self,dirpath,filename):
        im=Image.open(os.path.join(dirpath, filename))
        print time.asctime(), "thumbnailing...", filename, im.mode, im.size
        im.thumbnail((100,75))
        print time.asctime(), "showing...", filename, im.mode, im.size
        #im.show()
        self.Tkimage = ImageTk.PhotoImage(im)
        print "created"
        self.ImageLabel.config(image=self.Tkimage)
        self.ImageLabel.pack()
        self.FilenameLabel.config(text=filename)
        self.FilenameLabel.pack()
        self.StatusFrame.pack()
        self.root.update()

    
    def getstampedfilename(self, filename):
        fn, ft = os.path.splitext(filename)
        if ft.upper() in [".JPG", ".JPEG"] and \
               not (fn.upper().endswith("-DATED")):
            return fn + "-dated" + ft
        else:
            return None

    def timestamp(self, dirpath, original_filename, new_filename):
        full_original_filename = os.path.join(dirpath, original_filename)
        full_new_filename = os.path.join(dirpath, new_filename)
        font=ImageFont.truetype("arial.ttf", 40)
        datetext = GetFileDate(full_original_filename)
        im = Image.open(full_original_filename)
        im0 = Imprint(im, datetext, font=font, opacity=0.6, 
             color=(255,255,255))
        im0.save(full_new_filename, "JPEG")
        return datetext

def GetFileDate(file):
    """
    Returns the date associated with a file.
    For JPEG files, it will use the EXIF data, if available
    """
    try:
        import EXIF
        # EXIF.py from http://home.cfl.rr.com/genecash/digital_camera.html
        f = open(file, "rb")
        tags = EXIF.process_file(f)
        f.close()
        return str(tags['Image DateTime'])
    except (KeyError, ImportError):
        # EXIF not installed or no EXIF date available
        import os.path, time
        return time.ctime(os.path.getmtime(file))

def ReduceOpacity(im, opacity):
    """
    Returns an image with reduced opacity.
    """

    from PIL import ImageEnhance
    assert opacity >= 0 and opacity <= 1
    if im.mode != 'RGBA':
        im = im.convert('RGBA')
    else:
        im = im.copy()
    alpha = im.split()[3]
    alpha = ImageEnhance.Brightness(alpha).enhance(opacity)
    im.putalpha(alpha)
    return im

def Imprint(im, inputtext, font=None, color=None, opacity=.6, margin=(30,30)):
    """
    imprints a PIL image with the indicated text in lower-right corner
    """
    if im.mode != "RGBA":
        im = im.convert("RGBA")
    textlayer = Image.new("RGBA", im.size, (0,0,0,0))
    textdraw = ImageDraw.Draw(textlayer)
    textsize = textdraw.textsize(inputtext, font=font)
    textpos = [im.size[i]-textsize[i]-margin[i] for i in [0,1]]
    textdraw.text(textpos, inputtext, font=font, fill=color)
    if opacity != 1:
        textlayer = ReduceOpacity(textlayer,opacity)
    return Image.composite(textlayer, im, textlayer)
        
            
root = Tk.Tk()
myapp = MyApp(root)
root.mainloop()