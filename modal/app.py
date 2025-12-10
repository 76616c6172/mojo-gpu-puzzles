import modal

app = modal.App("76")
img = (
  modal.Image.from_registry("nvidia/cuda:12.4.0-base-ubuntu22.04")
  .apt_install("python-is-python3", "python3-pip")
  #.pip_install("max", index_url="https://packages.modular.com/max-nightly/pypi/simple")
  .pip_install("mojo", index_url="https://dl.modular.com/public/nightly/python/simple/", extra_options="--pre")
)


@app.function(image=img)
def main(): 
  # Use mojo python interop to call mojo code
  return("return the result")


