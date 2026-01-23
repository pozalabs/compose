import re
import sys


def fix_compose_imports(content: str) -> str:
    return re.sub(
        r"^import compose\.[a-zA-Z_.]+$",
        "import compose",
        content,
        flags=re.MULTILINE,
    )


def main() -> None:
    changed = False
    for filepath in sys.argv[1:]:
        with open(filepath) as f:
            original = f.read()

        fixed = fix_compose_imports(original)

        if fixed != original:
            with open(filepath, "w") as f:
                f.write(fixed)

            print(f"Fixed: {filepath}")
            changed = True

    sys.exit(int(changed))


if __name__ == "__main__":
    main()
