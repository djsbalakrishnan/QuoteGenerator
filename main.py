from PIL import Image, ImageDraw, ImageFont
import json
import os

def create_quote_image(quote_data, width=1080, height=1350, output_filename='quote_image.png'):
    """
    Creates an image with a black background and centered text based on input JSON,
    making better use of vertical space.
    
    Args:
        quote_data (dict): Dictionary containing quote content and author
        width (int): The width of the image in pixels
        height (int): The height of the image in pixels
        output_filename (str): The name of the output file
    
    Returns:
        None: The image is saved to disk
    """
    # Create a new black image with the specified dimensions
    img = Image.new('RGB', (width, height), color='black')
    draw = ImageDraw.Draw(img)
    
    # Load fonts - replace these paths with your actual font file paths
    try:
        # Try to load custom fonts if they exist
        regular_font_path = "fonts/PlayfairDisplay-Regular.ttf"
        italic_font_path = "fonts/PlayfairDisplay-Italic.ttf"
        author_font_path = "fonts/PlayfairDisplay-Regular.ttf"
        
        # Check if font files exist, otherwise use default
        if not os.path.exists(regular_font_path):
            print(f"Warning: Font file {regular_font_path} not found. Using default.")
            regular_font_path = None
        if not os.path.exists(italic_font_path):
            print(f"Warning: Font file {italic_font_path} not found. Using default.")
            italic_font_path = None
        if not os.path.exists(author_font_path):
            print(f"Warning: Font file {author_font_path} not found. Using default.")
            author_font_path = None
            
    except Exception as e:
        print(f"Error loading fonts: {e}")
        regular_font_path = None
        italic_font_path = None
        author_font_path = None
    
    # Set up font sizes
    main_text_size = 70  # Increased font size
    author_text_size = 26
    
    # Create font objects
    regular_font = ImageFont.truetype(regular_font_path, main_text_size) if regular_font_path else ImageFont.load_default()
    italic_font = ImageFont.truetype(italic_font_path, main_text_size) if italic_font_path else ImageFont.load_default()
    author_font = ImageFont.truetype(author_font_path, author_text_size) if author_font_path else ImageFont.load_default()
    
    content = quote_data.get('content', [])
    
    # ----------------
    # IMPROVED SPACING CALCULATIONS
    # ----------------
    
    # Calculate total available vertical space and distribute it better
    usable_height = height * 0.8  # Use 80% of image height for better spacing
    
    # Define spacing ratios for better distribution
    top_margin_ratio = 0.2    # Space at the top (20% of usable height)
    quote_section_ratio = 0.5  # Quote takes 50% of usable height
    bottom_section_ratio = 0.3 # Bottom section (line + author) takes 30% of usable height
    
    # Calculate actual spaces based on ratios
    top_margin = usable_height * top_margin_ratio
    quote_section_height = usable_height * quote_section_ratio
    bottom_section_height = usable_height * bottom_section_ratio
    
    # Line heights and inter-line spacing
    line_heights = []
    line_spacing = main_text_size * 0.7  # Increased spacing between lines
    
    # Calculate height of all text elements
    quote_text_height = 0
    for item in content:
        font = italic_font if item['style'] == 'italic' else regular_font
        text = item['text']
        bbox = draw.textbbox((0, 0), text, font=font)
        line_height = bbox[3] - bbox[1]
        line_heights.append(line_height)
        quote_text_height += line_height
    
    # Add spacing between lines
    total_quote_height = quote_text_height + (len(content) - 1) * line_spacing
    
    # Horizontal line and author settings
    horizontal_line_thickness = 3  # Slightly thicker line
    line_length = 120  # Length of the horizontal line
    
    # Get author text height
    author_text = quote_data.get('author', '')
    author_bbox = draw.textbbox((0, 0), author_text.upper(), font=author_font)
    author_height = author_bbox[3] - author_bbox[1]
    
    # Calculate starting position
    start_y = top_margin
    
    # Calculate even distribution within quote section
    if len(content) > 1:
        # Distribute lines evenly in the quote section
        quote_start_y = start_y + (quote_section_height - total_quote_height) / 2
    else:
        quote_start_y = start_y
    
    current_y = quote_start_y
    
    # Draw each line of the quote
    for i, item in enumerate(content):
        text = item['text']
        font = italic_font if item['style'] == 'italic' else regular_font
        text_width = draw.textlength(text, font=font)
        text_x = (width - text_width) // 2  # Center text horizontally
        
        # Draw the text
        draw.text((text_x, current_y), text, fill='white', font=font)
        
        # Move to next line position
        current_y += line_heights[i] + line_spacing
    
    # Position the horizontal line and author in the bottom section
    bottom_section_start = start_y + quote_section_height
    line_to_author_spacing = 40  # Space between line and author
    
    # Calculate positions for line and author
    line_y = bottom_section_start + (bottom_section_height - line_to_author_spacing - author_height) / 2
    line_start_x = (width - line_length) // 2
    line_end_x = line_start_x + line_length
    
    # Draw horizontal line
    draw.line([(line_start_x, line_y), (line_end_x, line_y)], fill='white', width=horizontal_line_thickness)
    
    # Draw author name in uppercase below the line
    author_text = quote_data.get('author', '').upper()
    author_width = draw.textlength(author_text, font=author_font)
    author_x = (width - author_width) // 2
    author_y = line_y + line_to_author_spacing
    
    draw.text((author_x, author_y), author_text, fill='white', font=author_font)
    
    # Save the image
    img.save(output_filename)
    print(f"Created quote image with better spacing as '{output_filename}'")
    return img

# Example usage
if __name__ == "__main__":
    # Sample input data
    quotes_data = [
        {
            "content": [
                {
                    "text": "Price is what",
                    "style": "normal"
                },
                {
                    "text": "you pay.",
                    "style": "italic"
                },
                {
                    "text": "Value is what",
                    "style": "normal"
                },
                {
                    "text": "you get.",
                    "style": "italic"
                }
            ],
            "author": "Warren Buffett"
        },
        {
            "content": [
                {
                    "text": "Patience",
                    "style": "normal"
                },
                {
                    "text": "creates wealth.",
                    "style": "italic"
                }
            ],
            "author": "Charlie Munger"
        },
        {
            "content": [
                {
                    "text": "Know what you own,",
                    "style": "normal"
                },
                {
                    "text": "and know",
                    "style": "italic"
                },
                {
                    "text": "why you own it.",
                    "style": "normal"
                }
            ],
            "author": "Peter Lynch"
        },
        {
            "content": [
                {
                    "text": "Margin",
                    "style": "normal"
                },
                {
                    "text": "of safety.",
                    "style": "italic"
                }
            ],
            "author": "Benjamin Graham"
        },
        {
            "content": [
                {
                    "text": "Avoid",
                    "style": "normal"
                },
                {
                    "text": "popular assets.",
                    "style": "italic"
                }
            ],
            "author": "Howard Marks"
        }
    ]

    
    # Create the image
    i = 0
    for quote_data in quotes_data:
        file_name = f'quote_image_{i}.png'
        create_quote_image(quote_data, output_filename=file_name)
        i += 1
