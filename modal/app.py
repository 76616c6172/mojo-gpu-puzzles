import modal

app = modal.App("76")
img = modal.Image.from_registry("modular/max-nvidia-full:latest")

@app.function(image=img)
def main(): return("Hello from 2025-12-07-modal!")


