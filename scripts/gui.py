import tkinter as tk
from tkinter import filedialog, messagebox, scrolledtext
from tkinterdnd2 import TkinterDnD, DND_FILES
from PIL import Image, ImageTk
from scripts.config import load_config, save_config
from scripts.parser import parse_image_metadata
from scripts.organizer import organize_images
import scripts.metadata_extractor as metadata_extractor
import scripts.metadata_extractor
import logging


def display_info(prompt_info, text_widgets):
    # Clear all text widgets
    for widget in text_widgets.values():
        if isinstance(widget, tk.Entry):
            widget.delete(0, tk.END)
        else:
            widget.delete('1.0', tk.END)

    def append_text(widget, text):
        if isinstance(widget, tk.Entry):
            widget.insert(tk.END, text)
        else:
            widget.insert(tk.END, text + '\n')

    # Models
    if hasattr(prompt_info, 'models') and prompt_info.models:
        model_text = '\n'.join([model.name for model in prompt_info.models])
        append_text(text_widgets['model'], model_text)

    # Samplers
    if hasattr(prompt_info, 'samplers') and prompt_info.samplers:
        sampler_names = '\n'.join([sampler.name for sampler in prompt_info.samplers])
        append_text(text_widgets['sampler'], sampler_names)
        for sampler in prompt_info.samplers:
            for param, value in sampler.parameters.items():
                if param in text_widgets:
                    append_text(text_widgets[param], value)

    # Prompts
    if hasattr(prompt_info, 'prompts') and prompt_info.prompts:
        prompt_text = '\n'.join([prompt.value for prompt in prompt_info.prompts])
        append_text(text_widgets['positive_prompt'], prompt_text)
    else:
        print('... looking')
        # Look for the specific CharacterNames in nodes in the metadata
        positive_prompt_text = metadata_extractor.get_workflow_node_data(prompt_info)
        # print(positive_prompt_text)

        prompt_text = '\n'.join(positive_prompt_text)
        append_text(text_widgets['positive_prompt'], prompt_text)
        print('prompt text:', prompt_text)

    # Negative Prompts
    if hasattr(prompt_info, 'negative_prompts') and prompt_info.negative_prompts:
        negative_prompt_text = '\n'.join([prompt.value for prompt in prompt_info.negative_prompts])
        append_text(text_widgets['negative_prompt'], negative_prompt_text)

    # Additional metadata
    if hasattr(prompt_info, 'metadata') and prompt_info.metadata:
        additional_metadata = '\n'.join([f"{k}: {v}" for k, v in prompt_info.metadata.items()])
        append_text(text_widgets['additional_metadata'], additional_metadata)

    # Unmodified parameters
    if hasattr(prompt_info, 'parameters') and prompt_info.parameters:
        params_text = '\n'.join([f"{k}: {v}" for k, v in prompt_info.parameters.items()])
        append_text(text_widgets['additional_metadata'], params_text)


def parse_image(file_path, text_widgets, image_label):
    try:
        # Load and display the image
        img = Image.open(file_path)
        img.thumbnail((200, 200))
        img = ImageTk.PhotoImage(img)
        image_label.config(image=img)
        image_label.image = img

        # Parse the file using the parser manager
        prompt_info = parse_image_metadata(file_path)
        if prompt_info:
            print(prompt_info)
            display_info(prompt_info, text_widgets)



    except Exception as e:
        logging.exception("Error reading file: %s", file_path)
        messagebox.showerror("Error", f"Error reading file: {file_path}\n{str(e)}")


def on_file_drop(event, text_widgets, image_label):
    file_path = event.data.strip('{}')
    parse_image(file_path, text_widgets, image_label)


def open_file_dialog(text_widgets, image_label):
    file_path = filedialog.askopenfilename(filetypes=[("PNG files", "*.png")])
    if file_path:
        parse_image(file_path, text_widgets, image_label)


def create_gui():
    root = TkinterDnD.Tk()
    root.title("Stable Diffusion Metadata Extractor")
    # ttk.Style().theme_use('equilux')

    frame = tk.Frame(root)
    frame.pack(pady=10, padx=10)

    # Load config
    config = load_config()

    # Image display
    image_frame = tk.Frame(frame)
    image_frame.grid(row=0, column=0, rowspan=10, padx=10, pady=10)
    image_label = tk.Label(image_frame)
    image_label.pack()

    # Drag and Drop area
    drop_area = tk.Label(frame, text="Drag Drop Image Here", relief="ridge", width=50, height=5)
    drop_area.grid(row=0, column=1, columnspan=2, pady=10)

    text_widgets = {}

    # Model
    tk.Label(frame, text="Model").grid(row=1, column=1, sticky=tk.W)
    text_widgets['model'] = tk.Entry(frame, width=50)
    text_widgets['model'].grid(row=1, column=2, pady=5)

    # Positive Prompt
    tk.Label(frame, text="Positive Prompt").grid(row=2, column=1, sticky=tk.W)
    text_widgets['positive_prompt'] = scrolledtext.ScrolledText(frame, wrap=tk.WORD, width=50, height=5)
    text_widgets['positive_prompt'].grid(row=2, column=2, pady=5)

    # Negative Prompt
    tk.Label(frame, text="Negative Prompt").grid(row=3, column=1, sticky=tk.W)
    text_widgets['negative_prompt'] = scrolledtext.ScrolledText(frame, wrap=tk.WORD, width=50, height=5)
    text_widgets['negative_prompt'].grid(row=3, column=2, pady=5)

    # Sampler
    tk.Label(frame, text="Sampler").grid(row=4, column=1, sticky=tk.W)
    text_widgets['sampler'] = tk.Entry(frame, width=50)
    text_widgets['sampler'].grid(row=4, column=2, pady=5)

    # Sampler Parameters
    sampler_params = ['seed', 'steps', 'cfg', 'scheduler', 'denoise']
    for i, param in enumerate(sampler_params, start=5):
        tk.Label(frame, text=param.title()).grid(row=i, column=1, sticky=tk.W)
        text_widgets[param] = tk.Entry(frame, width=50)
        text_widgets[param].grid(row=i, column=2, pady=5)

    # Additional Metadata
    tk.Label(frame, text="Additional Metadata").grid(row=10, column=0, columnspan=3, sticky=tk.W)
    text_widgets['additional_metadata'] = scrolledtext.ScrolledText(frame, wrap=tk.WORD, width=100, height=10)
    text_widgets['additional_metadata'].grid(row=11, column=0, columnspan=3, pady=5)

    btn_open = tk.Button(root, text="Open Image", command=lambda: open_file_dialog(text_widgets, image_label))
    btn_open.pack(pady=10)

    # Base directory for images
    tk.Label(frame, text="Base Images Directory").grid(row=12, column=0, sticky=tk.W)
    base_dir_entry = tk.Entry(frame, width=50)
    base_dir_entry.insert(0, config['base_dir'])
    base_dir_entry.grid(row=12, column=1, pady=5)

    # Output directory for organized images
    tk.Label(frame, text="Output Images Directory").grid(row=13, column=0, sticky=tk.W)
    output_dir_entry = tk.Entry(frame, width=50)
    output_dir_entry.insert(0, config['output_dir'])
    output_dir_entry.grid(row=13, column=1, pady=5)

    btn_organize = tk.Button(root, text="Organize", command=lambda: organize_images(base_dir_entry.get(), output_dir_entry.get()))
    btn_organize.pack(pady=10)

    def save_paths():
        config = {
            'base_dir': base_dir_entry.get(),
            'output_dir': output_dir_entry.get()
        }
        save_config(config)
        messagebox.showinfo("Info", "Paths saved successfully!")

    btn_save_paths = tk.Button(root, text="Save Paths", command=save_paths)
    btn_save_paths.pack(pady=10)

    # Enable drag and drop
    root.drop_target_register(DND_FILES)
    root.dnd_bind('<<Drop>>', lambda event: on_file_drop(event, text_widgets, image_label))

    root.mainloop()
