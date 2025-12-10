import modal

f = modal.Function.from_name("76", "main")  # app name + function name
result = f.remote('''call with some mojo gpu puzzle code to run here''')  # runs remotely, blocks until done, returns the value
print(result)
