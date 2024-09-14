import tkinter as tk
import textwrap
from tkinter import filedialog
from PIL import Image, ImageTk, ImageDraw, ImageFont


class MemeGeneratorApp:
    def __init__(self, root):
        self.root = root
        self.root.title("MemeMorph: Meme Generator")
        
        # Upload button
        self.upload_button = tk.Button(self.root, text="Upload Image", command=self.upload_image)
        self.upload_button.pack(pady=10)
        
        # Canvas to show uploaded image
        self.canvas = tk.Canvas(self.root, width=500, height=500, bg="gray")
        self.canvas.pack()
        
        # Text input fields
        self.top_text_label = tk.Label(self.root, text="Top Text")
        self.top_text_label.pack()
        self.top_text_entry = tk.Entry(self.root, width=40)
        self.top_text_entry.pack()
        
        self.bottom_text_label = tk.Label(self.root, text="Bottom Text")
        self.bottom_text_label.pack()
        self.bottom_text_entry = tk.Entry(self.root, width=40)
        self.bottom_text_entry.pack()
        
        # Generate meme button
        self.generate_button = tk.Button(self.root, text="Generate Meme", command=self.add_text_to_image)
        self.generate_button.pack(pady=10)
        
        self.img_path = None
        self.image = None
        self.tk_image = None

    def upload_image(self):
        self.img_path = filedialog.askopenfilename()
        if self.img_path:
            self.image = Image.open(self.img_path)
            self.image = self.image.resize((500, 500), Image.Resampling.LANCZOS)
            self.tk_image = ImageTk.PhotoImage(self.image)
            self.canvas.create_image(0, 0, anchor=tk.NW, image=self.tk_image)



    def add_text_to_image(self):
        if not self.img_path:
            print("No image uploaded.")
            return
        
        top_text = self.top_text_entry.get().upper()
        bottom_text = self.bottom_text_entry.get().upper()
        
        # Load the image again
        img = Image.open(self.img_path)
        img = self.image.resize((500, 500), Image.Resampling.LANCZOS)
        draw = ImageDraw.Draw(img)
        
        # Load a font (Make sure you have a .ttf file in the same folder or use any other font path)
        font = ImageFont.truetype("impact.ttf", 40)
        
        # Function to wrap text after 60 characters
        def wrap_text(text, width):
            return "\n".join(textwrap.wrap(text, width=width))
        
        # Wrap the top and bottom texts to fit within 60 characters
        top_text_wrapped = wrap_text(top_text, 60)
        bottom_text_wrapped = wrap_text(bottom_text, 60)
        
        # Draw centered top text
        top_text_bbox = draw.textbbox((0, 0), top_text_wrapped, font=font)
        top_text_width = top_text_bbox[2] - top_text_bbox[0]
        draw.text(((img.width - top_text_width) / 2, 10), top_text_wrapped, font=font, fill="white", stroke_width=2, stroke_fill="black")
        
        # Draw centered bottom text
        bottom_text_bbox = draw.textbbox((0, 0), bottom_text_wrapped, font=font)
        bottom_text_width = bottom_text_bbox[2] - bottom_text_bbox[0]
        bottom_text_height = bottom_text_bbox[3] - bottom_text_bbox[1]
        draw.text(((img.width - bottom_text_width) / 2, img.height - bottom_text_height - 40), bottom_text_wrapped, font=font, fill="white", stroke_width=2, stroke_fill="black")
        
        # Show updated image with text
        self.image_with_text = img
        self.tk_image_with_text = ImageTk.PhotoImage(img)
        self.canvas.create_image(0, 0, anchor=tk.NW, image=self.tk_image_with_text)


# Run the application
if __name__ == "__main__":
    root = tk.Tk()
    app = MemeGeneratorApp(root)
    root.mainloop()
