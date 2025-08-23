import os

def print_tree(startpath, indent="", depth=0, max_depth=4):
    """Recursively prints the folder tree structure up to max_depth levels."""
    if depth > max_depth:
        return
    items = sorted(os.listdir(startpath))
    for index, item in enumerate(items):
        if item == ".git"  :  # skip .git folder
            continue
        path = os.path.join(startpath, item)
        connector = "└── " if index == len(items) - 1 else "├── "
        print(indent + connector + item)
        if os.path.isdir(path) and depth < max_depth:
            extension = "    " if index == len(items) - 1 else "│   "
            print_tree(path, indent + extension, depth + 1, max_depth)

if __name__ == "__main__":
    folder = input("Enter folder path: ").strip() or "."
    print(folder)
    print_tree(folder, max_depth=4)  # change depth here if needed
