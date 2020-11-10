import pathlib
import tkinter as tk
from tkinter import filedialog
from PIL import Image, ImageTk


class Application(tk.Frame):

    def __init__(self, master=None):
        super().__init__(master)
        self.master = master
        self.pack(fill=tk.BOTH, expand=1)

        # variables
        self.records = []
        self.records_index = 0
        self.record_to_text = {}
        self.record_to_image = {}
        self.ocr_doc_path = None

        # create widgets
        self.create_widgets()

    def create_widgets(self):

        self.ocr_doc_path_var = tk.StringVar()
        self.ocr_doc_path_label = tk.Label(self, text='OCR Path')
        self.ocr_doc_path_label.grid(row=1, column=0)
        self.ocr_doc_path_entry = tk.Entry(self, width=100, textvariable=self.ocr_doc_path_var)
        self.ocr_doc_path_entry.grid(row=1, column=1, columnspan=10)
        self.btn_browse_folder = tk.Button(self, text="Browse Folder", command=self.set_folder_path)
        self.btn_browse_folder.grid(row=1, column=11)

        self.btn_retrieve = tk.Button(self, text='Retrieve Records', command=self.get_records)
        self.btn_retrieve.grid(row=2, column=0, columnspan=4, rowspan=1)
        self.record_cnt = tk.IntVar()
        self.cnt_entry = tk.Entry(self, textvariable=self.record_cnt, state=tk.DISABLED)
        self.cnt_entry.grid(row=2, column=4)

        self.btn_prev = tk.Button(self, text='Previous Record', command=self.get_previous_record)
        self.btn_prev.grid(row=3, column=0, columnspan=3)
        self.btn_next = tk.Button(self, text='Next Record', command=self.get_next_record)
        self.btn_next.grid(row=3, column=5, columnspan=3)

        self.image_window_error = tk.StringVar()
        self.image_window = tk.Label(self, textvariable=self.image_window_error)
        self.image_window.grid(row=4, column=0, rowspan=4, columnspan=10, sticky=tk.W + tk.E + tk.N + tk.S,
                               padx=5, pady=5)

        self.text_content = tk.StringVar()
        self.text_window = tk.Text(self, height=60, width=100)
        self.text_window.grid(row=4, column=10, rowspan=4, columnspan=10, sticky=tk.W + tk.E + tk.N + tk.S,
                              padx=5, pady=5)

    def set_folder_path(self):
        path = filedialog.askdirectory()
        self.ocr_doc_path = pathlib.Path(path)
        self.ocr_doc_path_var.set(filedialog.askdirectory())

    def get_records(self):
        if not self.ocr_doc_path:
            return None
        recs = set()
        for p in self.ocr_doc_path.iterdir():
            if p.is_file():
                basename = p.name.split('.')[0]
                recs.add(basename)  # ignore extensions
                if p.name.endswith('.txt'):
                    self.record_to_text[basename] = p
                else:
                    self.record_to_image[basename] = p
        self.records = list(recs)
        self.record_cnt.set(len(self.records))
        self.records_index = -1

    def _get_image(self, rec):
        img_path = self.record_to_image.get(rec, None)
        if not img_path:
            self.image_window_error.set(f'Not image found for file {rec}')
            return
        try:
            img = Image.open(str(img_path))
        except Exception as e:
            self.image_window_error.set(f'Exception for {rec}: {e}')
            return
        img.thumbnail((1280, 1280))
        img = ImageTk.PhotoImage(img)
        self.image_window.configure(image=img)
        self.image_window.image = img

    def _get_text(self, rec):
        text_file = self.record_to_text.get(rec, None)
        self.text_window.delete(1.0, tk.END)
        if not text_file:
            self.text_window.insert(1.0, f'No file found for {rec}.')
            return None
        with open(text_file, encoding='utf8') as fh:
            self.text_window.insert(1.0, fh.read())

    def get_next_record(self):
        if not self.records:
            return
        self.records_index = (self.records_index + 1) % len(self.records)
        rec = self.records[self.records_index]
        self._get_image(rec)
        self._get_text(rec)

    def get_previous_record(self):
        if not self.records:
            return
        self.records_index = (self.records_index - 1) % len(self.records)
        rec = self.records[self.records_index]
        self._get_image(rec)
        self._get_text(rec)


root = tk.Tk()
root.geometry('2000x1800')
app = Application(master=root)
app.mainloop()
