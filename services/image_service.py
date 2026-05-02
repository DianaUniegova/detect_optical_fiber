import os

def process_image(path):
    filename = os.path.basename(path)
    result_path = os.path.join("results", filename)

    # тут буде твоя модель
    # поки що просто копія
    import shutil
    shutil.copy(path, result_path)

    return {
        "type": "image",
        "file": path,
        "result_image": result_path
    }