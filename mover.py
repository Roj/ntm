from pathlib import Path
import shutil

def copy():
    img_dir = Path("new_imgs")
    images = img_dir.glob("*")
    target_dir = Path("img")
    for i, f in enumerate(images):
        new_name = f"image{i}{f.suffix}"
        print(f"""["{new_name}", ["{f.stem}"]], """)
        #f.rename(target_dir / new_name)
        shutil.copy(f, target_dir / new_name)



