import tkinter as tk
from tkinter import filedialog, messagebox, ttk
from moviepy.editor import ImageClip, AudioFileClip
from PIL import Image
from send2trash import send2trash
from os import path
from sys import exit, stderr


def safe_send_to_trash(file_path):
    # Convert forward slashes to backslashes
    file_path = file_path.replace('/', '\\')

    # Check if the file exists
    if not path.exists(file_path):
        print(f"File does not exist: {file_path}", file=stderr)
        return

    # Attempt to send the file to trash
    try:
        send2trash(file_path)
        print(f"File sent to trash: {file_path}", file=stderr)
    except Exception as e:
        print(f"Failed to send file to trash: {e}", file=stderr)


class AudioVideoConverterApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Audio to Video Converter")
        self.root.geometry("640x480")  # Set initial size

        # Set a window icon here if you have one
        # self.root.iconbitmap('path_to_icon.ico')

        style = ttk.Style()
        style.configure('TButton', font=('Arial', 10))
        style.configure('TLabel', font=('Arial', 12))

        # Define Grid Layout
        root.columnconfigure(1, weight=1)
        for i in range(4):
            root.rowconfigure(i, weight=1)

        # Audio selection
        self.audio_label = ttk.Label(root, text="No audio file selected")
        self.audio_label.grid(row=0, column=0, columnspan=2, padx=10, pady=5, sticky="ew")
        ttk.Button(root, text="Select Audio File", command=self.select_audio).grid(row=0, column=2, padx=10, pady=5)

        # Image selection
        self.image_label = ttk.Label(root, text="No image file selected")
        self.image_label.grid(row=1, column=0, columnspan=2, padx=10, pady=5, sticky="ew")
        ttk.Button(root, text="Select Image File", command=self.select_image).grid(row=1, column=2, padx=10, pady=5)

        # Output directory selection
        self.output_label = ttk.Label(root, text="No output directory selected")
        self.output_label.grid(row=2, column=0, columnspan=2, padx=10, pady=5, sticky="ew")
        ttk.Button(root, text="Select Output Directory", command=self.select_output_directory).grid(row=2, column=2,
                                                                                                    padx=10, pady=5)

        # Start conversion button
        ttk.Button(root, text="Start Conversion", command=self.start_conversion).grid(row=3, column=0, columnspan=3,
                                                                                      padx=10, pady=10)

        # Make window resizable
        root.resizable(True, True)

    def select_audio(self):
        self.audio_path = filedialog.askopenfilename(filetypes=[("Audio Files", "*.mp3 *.wav")])
        if self.audio_path:
            self.audio_label.config(text=path.basename(self.audio_path))

    def select_image(self):
        self.image_path = filedialog.askopenfilename(filetypes=[("Image Files", "*.jpg *.jpeg *.png")])
        if self.image_path:
            self.image_label.config(text=path.basename(self.image_path))

    def select_output_directory(self):
        self.output_directory = filedialog.askdirectory()
        if self.output_directory:
            self.output_label.config(text=self.output_directory)

    def start_conversion(self):
        if not self.audio_path or not self.image_path or not self.output_directory:
            messagebox.showerror("Error", "Please select an audio file, an image file, and an output directory.")
            return

        output_file_name = path.splitext(path.basename(self.audio_path))[0] + ".mp4"
        output_path = path.join(self.output_directory, output_file_name)
        create_video(self.image_path, self.audio_path, output_path)
        messagebox.showinfo("Success", f"Video created successfully: {output_path}")


def convert_to_jpg(image_path):
    if image_path.lower().endswith('.png'):
        jpg_path = image_path.rsplit('.', 1)[0] + '.jpg'
        with Image.open(image_path) as img:
            rgb_im = img.convert('RGB')
            rgb_im.save(jpg_path)
        return jpg_path
    return image_path


def create_video(image_path, audio_path, output_path):
    # Check if the image format is valid
    if not image_path.lower().endswith(('.jpg', '.jpeg', '.png')):
        print("Unsupported image format. Please use JPG, JPEG, or PNG.", file=stderr)
        exit(1)

    # Convert PNG to JPG if necessary
    original_image_path = image_path
    image_path = convert_to_jpg(image_path)

    # Check if the audio format is valid
    if not audio_path.lower().endswith(('.mp3', '.wav')):
        print("Unsupported audio format. Please use MP3 or WAV.", file=stderr)
        exit(1)

    if not output_path.lower().endswith(".mp4"):
        print("Unsupported output format. Please use MP4.", file=stderr)
        exit(1)

    # Load the image and the audio
    image_clip = ImageClip(image_path)
    audio_clip = AudioFileClip(audio_path)

    # Set the audio of the image clip as the audio clip
    video_clip = image_clip.set_audio(audio_clip)

    # Set the duration of the video clip to the duration of the audio clip
    video_clip = video_clip.set_duration(audio_clip.duration)

    # Write the result to a file
    video_clip.write_videofile(output_path, codec="hevc_nvenc", fps=1)

    print(f"Video created successfully: {output_path}")

    # Clean up if a new JPG was created
    if original_image_path != image_path:
        safe_send_to_trash(image_path)


if __name__ == "__main__":
    root = tk.Tk()
    app = AudioVideoConverterApp(root)
    root.mainloop()
