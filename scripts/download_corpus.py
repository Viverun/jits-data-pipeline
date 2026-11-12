import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from legal_ai_toolkit.cli import main


if __name__ == "__main__":
    sys.argv = ["legal-ai", "download", *sys.argv[1:]]
    main()
