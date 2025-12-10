import modal

f = modal.Function.from_name("76", "main")  # app name + function name
result = f.remote()  # runs remotely, blocks until done, returns the value
print(result)
