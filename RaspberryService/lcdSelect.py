import time
from PIL import Image, ImageDraw, ImageFont
from gpiozero import RotaryEncoder, Button
from lib import LCD_1inch69

# Initialize display
disp = LCD_1inch69.LCD_1inch69()
disp.Init()
disp.clear()
disp.bl_DutyCycle(100)  # Backlight at 100% brightness

Schriftart = ImageFont.truetype("./Font/Font02.ttf", 32)

# Rotary Encoder and Button GPIO pins
clk_pin = 17
dt_pin = 22
sw_pin = 23

# Initialize Rotary Encoder and Button
encoder = RotaryEncoder(clk_pin, dt_pin)
button = Button(sw_pin)

# Global variables
current_position = 0
num_items = 0
selected_index = None
header_position = 0
input_list = []  # List for items
header_text = ""  # Used to pass header text to callback functions

# Track the last state of the encoder
last_encoder_value = 0

def update_display():
    global header_position
    image1 = Image.new("RGB", (disp.width, disp.height), "WHITE")
    image1 = image1.rotate(-90, expand=True)  # Rotation because of side image
    draw = ImageDraw.Draw(image1)
    
    header_width = disp.width - 20  # Margin
    header_lines = []

    # Header splitting
    current_line = ""
    for char in header_text:
        test_line = current_line + char
        width, _ = draw.textsize(test_line, font=Schriftart)
        if width > header_width:
            header_lines.append(current_line)
            current_line = char
        else:
            current_line = test_line
    if current_line:
        header_lines.append(current_line)
    
    header_position = (header_position + 1) % len(header_lines)
    
    # Header
    y_position = 0
    for i, line in enumerate(header_lines):
        draw.text((25, y_position), line, font=Schriftart, fill="BLACK")
        y_position += Schriftart.getsize(line)[1]
    
    # Header underline
    underline_y = y_position
    underline_start = 25
    underline_end = min(disp.width - 25, underline_start + header_width)
    draw.line([(underline_start, underline_y), (underline_end, underline_y)], fill="BLACK", width=2)
    
    # List items
    for i in range(num_items):
        text = '> ' + input_list[i] if i == current_position else '  ' + input_list[i]
        y_position = len(header_lines) * Schriftart.getsize(header_lines[0])[1] + i * Schriftart.getsize(text)[1] + 50
        draw.text((25, y_position), text, font=Schriftart, fill="BLACK")

    disp.ShowImage(image1)

def clear_display():
    disp.clear()

def on_encoder_rotate():
    global current_position, last_encoder_value
    encoder_value = encoder.value
    if encoder_value != last_encoder_value:
        if encoder_value > last_encoder_value:
            current_position = (current_position + 1) % num_items
        else:
            current_position = (current_position - 1) % num_items
        last_encoder_value = encoder_value
        update_display()

def on_button_press():
    global selected_index
    selected_index = current_position
    clear_display()

def lcdUserListSelect(lst, header_text_input):
    global current_position, num_items, selected_index, input_list, header_text, last_encoder_value

    # Reset
    input_list = lst
    num_items = len(input_list)
    current_position = 0
    selected_index = None
    header_text = header_text_input
    last_encoder_value = encoder.value  # Initialize last encoder value

    # Assign callback functions
    encoder.when_rotated = on_encoder_rotate
    button.when_pressed = on_button_press

    clear_display()
    update_display()

    # Waiting for user input
    while selected_index is None:
        time.sleep(0.01)  # Adjust as needed

    blank_image = Image.new("RGB", (disp.width, disp.height), "WHITE")
    blank_image = blank_image.rotate(-90, expand=True)
    disp.ShowImage(blank_image)
    clear_display()
    return selected_index
