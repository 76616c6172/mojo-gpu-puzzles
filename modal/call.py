import modal
from pathlib import Path

f = modal.Function.from_name("76", "main")

puzzle_num = input("Enter puzzle number: ").strip()
padded = puzzle_num.zfill(2)
puzzle_path = Path(f"problems/p{padded}/p{padded}.mojo")

if not puzzle_path.exists():
    print(f"File not found: {puzzle_path}")
    exit(1)

print(f"Running puzzle {puzzle_num} on Modal GPU...\n")
mojo_code = puzzle_path.read_text()
result = f.remote(mojo_code)

if result["success"]:
    print("--- SUCCESS ---")
    print(f"Puzzle {puzzle_num} completed successfully!\n")
else:
    print("--- FAILURE ---")
    print(f"Puzzle {puzzle_num} failed (exit code: {result['exit_code']})\n")

if result["stdout"]:
    print("--- STDOUT ---")
    formatted = result["stdout"].replace("out:", "\tgot: ").replace("expected:", "\twant:")
    print(formatted)

if result["stderr"]:
    print("--- WARNINGS ---:")
    print(result["stderr"])
