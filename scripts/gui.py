import tkinter as tk
from tkinter import filedialog, messagebox, scrolledtext
from tkinterdnd2 import TkinterDnD, DND_FILES
from PIL import Image, ImageTk
from scripts.parser import parse_image_metadata
from scripts.organizer import organize_images
import scripts.metadata_extractor as metadata_extractor
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
        # Look for the specific CharacterNames in nodes in the metadata
        positive_prompt_text = metadata_extractor.get_workflow_node_data(prompt_info)
        prompt_text = '\n'.join(positive_prompt_text)
        append_text(text_widgets['positive_prompt'], prompt_text)

    # Negative Prompts
    if hasattr(prompt_info, 'negative_prompts') and prompt_info.negative_prompts:
        negative_prompt_text = '\n'.join([prompt.value for prompt in prompt_info.negative_prompts])
        append_text(text_widgets['negative_prompt'], negative_prompt_text)

    # Additional metadata
    if hasattr(prompt_info, 'metadata') and prompt_info.metadata:
        additional_metadata = '\n'.join([k + ": " + str(v) for k, v in prompt_info.metadata.items()])
        append_text(text_widgets['additional_metadata'], additional_metadata)

    # Unmodified parameters
    if hasattr(prompt_info, 'parameters') and prompt_info.parameters:
        params_text = '\n'.join([k + ": " + str(v) for k, v in prompt_info.parameters.items()])
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
            display_info(prompt_info, text_widgets)

    except Exception as e:
        logging.exception("Error reading file: " + file_path)
        messagebox.showerror("Error", "Error reading file: " + file_path + "\n" + str(e))


def on_file_drop(event, text_widgets, image_label):
    file_path = event.data.strip('{}')
    parse_image(file_path, text_widgets, image_label)


def open_file_dialog(text_widgets, image_label):
    file_path = filedialog.askopenfilename(filetypes=[("PNG files", "*.png")])
    if file_path:
        parse_image(file_path, text_widgets, image_label)


def create_gui(config, save_config):
    root = TkinterDnD.Tk()
    root.title("Stable Diffusion Metadata Extractor")

    frame = tk.Frame(root)
    frame.pack(pady=10, padx=10)

    # Preview Image Metadata label
    tk.Label(frame, text="Preview Image Metadata", font=("Arial", 14)).pack(pady=10)

    # Image Input Group
    image_input_frame = tk.LabelFrame(frame, text="Image Input", padx=10, pady=10)
    image_input_frame.pack(fill="x", pady=10)

    # Open image button
    btn_open = tk.Button(image_input_frame, text="Open Image", command=lambda: open_file_dialog(text_widgets, image_label))
    btn_open.grid(row=0, column=0, columnspan=3, pady=10)

    # Image display
    image_label = tk.Label(image_input_frame)
    image_label.grid(row=1, column=0, padx=10, pady=10)

    # Drag and Drop area
    drop_area = tk.Label(image_input_frame, text="Drag Drop Image Here", relief="ridge", width=50, height=5)
    drop_area.grid(row=1, column=1, columnspan=2, pady=10)

    image_input_frame.grid_columnconfigure(0, weight=1)
    image_input_frame.grid_columnconfigure(1, weight=1)
    image_input_frame.grid_columnconfigure(2, weight=1)

    text_widgets = {}

    # Metadata Group
    metadata_frame = tk.LabelFrame(frame, text="Metadata", padx=10, pady=10)
    metadata_frame.pack(fill="x", pady=10)

    def create_labeled_widget(parent, label_text, row, widget_type=tk.Entry, **options):
        tk.Label(parent, text=label_text).grid(row=row, column=0, sticky=tk.W)
        widget = widget_type(parent, **options)
        widget.grid(row=row, column=1, pady=5, sticky=tk.W + tk.E)
        return widget

    text_widgets['model'] = create_labeled_widget(metadata_frame, "Model", 0)
    text_widgets['positive_prompt'] = create_labeled_widget(metadata_frame, "Positive Prompt", 1, scrolledtext.ScrolledText, wrap=tk.WORD, width=50, height=5)
    text_widgets['negative_prompt'] = create_labeled_widget(metadata_frame, "Negative Prompt", 2, scrolledtext.ScrolledText, wrap=tk.WORD, width=50, height=5)
    text_widgets['sampler'] = create_labeled_widget(metadata_frame, "Sampler", 3)

    sampler_params = ['seed', 'steps', 'cfg', 'scheduler', 'denoise']
    for i, param in enumerate(sampler_params, start=4):
        text_widgets[param] = create_labeled_widget(metadata_frame, param.title(), i)

    tk.Label(metadata_frame, text="Additional Metadata").grid(row=10, column=0, columnspan=2, sticky=tk.W)
    text_widgets['additional_metadata'] = scrolledtext.ScrolledText(metadata_frame, wrap=tk.WORD, width=100, height=10)
    text_widgets['additional_metadata'].grid(row=11, column=0, columnspan=2, pady=5, sticky=tk.W + tk.E)

    metadata_frame.grid_columnconfigure(1, weight=1)

    # Organize Section
    organize_frame = tk.LabelFrame(frame, text="Organize Images", padx=10, pady=10)
    organize_frame.pack(fill="x", pady=10)

    tk.Label(organize_frame, text="This section is used for organizing a directory of images and placing them into subdirectories based on keywords defined in characters.txt and locations.txt.").grid(row=0, column=0, columnspan=3, pady=5)

    # Input images directory
    tk.Label(organize_frame, text="Input Images Directory").grid(row=1, column=0, sticky=tk.W)
    input_dir_entry = tk.Entry(organize_frame, width=50)
    input_dir_entry.insert(0, config['base_dir'])
    input_dir_entry.grid(row=1, column=1, pady=5, sticky=tk.W + tk.E)

    # Output images directory
    tk.Label(organize_frame, text="Output Images Directory").grid(row=2, column=0, sticky=tk.W)
    output_dir_entry = tk.Entry(organize_frame, width=50)
    output_dir_entry.insert(0, config['output_dir'])
    output_dir_entry.grid(row=2, column=1, pady=5, sticky=tk.W + tk.E)

    btn_save_paths = tk.Button(organize_frame, text="Save Paths", command=lambda: save_paths(input_dir_entry, output_dir_entry, save_config))
    btn_save_paths.grid(row=3, column=0, columnspan=2, pady=5)

    btn_organize = tk.Button(organize_frame, text="Organize", command=lambda: organize_images(input_dir_entry.get(), output_dir_entry.get(), config['node_defaults']))
    btn_organize.grid(row=4, column=0, columnspan=2, pady=10)

    organize_frame.grid_columnconfigure(1, weight=1)

    # Enable drag and drop
    root.drop_target_register(DND_FILES)
    root.dnd_bind('<<Drop>>', lambda event: on_file_drop(event, text_widgets, image_label))

    root.mainloop()


def save_paths(input_dir_entry, output_dir_entry, save_config):
    config = {
        'base_dir': input_dir_entry.get(),
        'output_dir': output_dir_entry.get()
    }
    save_config(config)
    messagebox.showinfo("Info", "Paths saved successfully!")
