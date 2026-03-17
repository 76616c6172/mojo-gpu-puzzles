import modal
import sys
from pathlib import Path

f = modal.Function.from_name("76", "main")

if len(sys.argv) > 1:
    puzzle_num = sys.argv[1].strip()
else:
    try:
        puzzle_num = input("Enter puzzle number: ").strip()
    except EOFError as exc:
        raise SystemExit("Provide a puzzle number interactively or run `uv run modal/call.py 1`.") from exc

padded = puzzle_num.zfill(2)
puzzle_path = Path(f"problems/p{padded}/p{padded}.mojo")

if not puzzle_path.exists():
    print(f"File not found: {puzzle_path}")
    exit(1)

print(f"\nPuzzle {puzzle_num}")
print("-" * 40)
mojo_code = puzzle_path.read_text()

for update in f.remote_gen(mojo_code):
    if update["status"] == "gpu_info":
        name, mem_mb = update["gpu"].split(", ")
        mem_gb = int(mem_mb) / 1024
        print(f"GPU: {name} ({mem_gb:.1f} GB)")
    
    elif update["status"] == "compiling":
        print("Compiling and running...")
    
    elif update["status"] == "complete":
        print()
        if update["success"]:
            print("SUCCESS")
        else:
            print(f"FAILED (exit code {update['exit_code']})")

        if update["stdout"]:
            formatted = update["stdout"].replace("out:", "\tgot: ").replace("expected:", "\twant:")
            print(formatted)

        if update["stderr"]:
            print("Warnings:")
            print(update["stderr"])

print("-" * 40)
