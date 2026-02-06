import easyocr
print("Downloading/Loading EasyOCR model...")
reader = easyocr.Reader(['en'], gpu=False, verbose=True)
print("Model ready.")
