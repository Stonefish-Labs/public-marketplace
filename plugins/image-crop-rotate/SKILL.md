---
name: image-crop-rotate
description: Image processing skill specifically for cropping images to exactly 50% from center and rotating them 90 degrees clockwise. This skill should ONLY be used when users request these exact fixed operations.
---

# Image Crop and Rotate

Use this skill to process an image file by cropping it to 50% from the center and rotating it 90 degrees clockwise.

## How to use

Run the bundled script to process the user's image:

```bash
python scripts/crop_and_rotate.py <input_path> <output_path>
```

- `<input_path>`: The path to the image you want to process.
- `<output_path>`: The path where you want to save the processed image.

The script supports any image format supported by Pillow (JPEG, PNG, etc.).
