import tkinter as tk
from tkinter import ttk, filedialog
from tkinter.messagebox import showerror
from PIL import Image, ImageTk, ImageFont, ImageDraw


class App(tk.Tk):
    img: ImageTk.PhotoImage | None = None
    original_img: Image.Image | None = None
    resized_img: Image.Image | None = None
    file_name: str | None = None
    img_container: int = 0
    FILE_TYPES = [
        ("Jpgs", "*.jpg"), ("Jpgs", "*.jpeg"), ("Pngs", "*.png"),
        ("Gifs", "*.gif")
    ]
    x_axis: float = 0
    font_size: float = 0
    ratio: float = 0

    def __init__(self):
        super().__init__()
        # Window
        self.title("Watermarker")
        self.geometry("1500x930")
        self.config(pady=50, padx=50)

        # Image Load
        self.image_load_button = ttk.Button(
            self,
            text="Open Image",
            width=16,
            command=self.load_image,
        )
        self.image_load_button.grid(
            row=0, column=2, sticky="NW"
        )

        self.image_label = ttk.Label(self, text=self.file_name, width=21)
        self.image_label.grid(
            row=0, column=3, sticky="N")

        self.image_screen = tk.Canvas(
            self,
            width=800,
            height=800,
            highlightthickness=0
        )
        self.image_screen.grid(
            row=0, rowspan=2, column=1, padx=20
        )

        # Watermark Section
        self.watermark_label = ttk.Label(
            self,
            text="Watermark Text",
            font=("Arial", 18, "bold")
        )
        self.watermark_label.grid(
            row=0, rowspan=1, column=2, columnspan=3, sticky="S", pady=20
        )

        self.watermark_text = tk.Text(
            self, width=45, name="watermark_text")
        self.watermark_text.grid(
            row=1, column=2, columnspan=2, sticky="N"
        )

        # Watermark position - font size
        self.font_size_label = ttk.Label(self, text="Font Size:")
        self.font_size_label.grid(
            row=1, column=2, sticky="SE", padx=50
        )

        font_size_var = tk.IntVar()
        self.font_size_box = ttk.Entry(
            self, name="font-size", textvariable=font_size_var, width=3,
            justify="center"
        )
        self.font_size_box.grid(row=1, column=2, sticky="SE")

        self.x_axis_label = ttk.Label(self, text="Move Text:")
        self.x_axis_label.grid(
            row=1, column=3, sticky="SE", padx=50
        )

        x_axis_var = tk.IntVar()
        self.x_axis_box = ttk.Entry(
            self, name="x_axis", textvariable=x_axis_var, width=3,
            justify="center"
        )
        self.x_axis_box.grid(row=1, column=3, sticky="SE")

        self.save_btn = ttk.Button(
            self,
            text="Save Image",
            width=19,
            command=self.save_img,
            state="disabled"
        )

        self.save_btn.grid(
            row=2, rowspan=3, column=3, sticky="E", pady=20
        )

        self.preview_btn = ttk.Button(
            self,
            text="Preview Image",
            width=20,
            command=lambda: self.preview_image(),
            state="disabled"
        )

        self.preview_btn.grid(
            row=2, rowspan=3, column=2, sticky="E"
        )

    def draw_text(self, image, preview=None):
        watermark_text = self.watermark_text.get("1.0", tk.END)
        transparent_text: Image.Image | None = None
        try:
            transparent_text = Image.new(
                size=image.size,
                mode="RGBA",
                color=(255, 255, 255, 0)
            )
        except AttributeError:
            showerror("Bad bad panda!", message="Open an image firstly!")

        try:
            if preview is None:
                self.x_axis = int(self.x_axis_box.get()) * self.ratio
                self.font_size = int(self.font_size_box.get()) * self.ratio
            else:
                self.x_axis = int(self.x_axis_box.get())
                self.font_size = int(self.font_size_box.get())
        except ValueError:
            showerror("Bad bad panda!", message="Use only numbers in boxes!")

        draw = ImageDraw.Draw(transparent_text)
        font = ImageFont.truetype("Ubuntu-B.ttf", round(self.font_size))
        draw.text(
            (
                self.x_axis,
                round(image.height / 2.5)
            ),
            watermark_text,
            fill=(255, 255, 255, 85),  # rgb
            font=font,
            align="right",

        )

        image = image.convert(mode="RGBA")
        combine_img = Image.alpha_composite(
            image, transparent_text
        )

        return combine_img.convert(mode="RGB")

    def save_img(self):
        file_path = filedialog.asksaveasfilename(filetypes=self.FILE_TYPES)
        combine_img = self.draw_text(self.original_img)

        try:
            combine_img.save(file_path)
        except AttributeError:
            showerror(
                "Bad bad panda!", message="Open and edit an image firstly!"
            )
        except ValueError:
            pass

    def preview_image(self):
        self.image_screen.delete("img_container")
        combine_img = self.draw_text(self.resized_img, preview=True)
        img = ImageTk.PhotoImage(combine_img)

        self.image_screen.create_image(
            (img.width(), img.height()), anchor=tk.SE,
            image=img, tags="img_container"
        )
        self.image_screen.image = img

    def load_image(self):
        try:
            file_location = filedialog.askopenfilename(filetypes=self.FILE_TYPES)
            self.set_file_name(file_location)
            self.image_screen.delete("img_container")

            with Image.open(file_location) as image:
                self.original_img = image
                self.resized_img = self.resize_image(self.original_img)
                self.ratio = self.original_img.width / self.resized_img.width
                self.img = ImageTk.PhotoImage(self.resized_img)

                self.img_container = self.image_screen.create_image(
                    (self.img.width(), self.img.height()), anchor=tk.SE,
                    image=self.img, tags="img_container"
                )

            self.save_btn.config(state="enabled")
            self.preview_btn.config(state="enabled")
        except AttributeError:
            pass

    def set_file_name(self, file_location):
        file_name = file_location.split("/")[-1]
        self.file_name = file_name if len(file_name) < 20 else file_name[:21]
        self.image_label.config(text=self.file_name)

    @staticmethod
    def resize_image(image: Image):
        if image.width > 800 and image.width >= image.height:
            ratio = image.width / 800
            new_width = round(image.width / ratio)
            new_height = round(image.height / ratio)
            image = image.resize((new_width, new_height))

        elif image.height > 800 and image.width < image.height:
            ratio = image.height / 800
            new_width = round(image.width / ratio)
            new_height = round(image.height / ratio)
            image = image.resize((new_width, new_height))

        return image
