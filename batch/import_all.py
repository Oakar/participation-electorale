"""
Orchestrateur d'import : geo puis elections.

Usage:
    python batch/import_all.py
"""

import import_geo
import import_elections


def main() -> None:
    import_geo.run()
    import_elections.run()
    print("=== Tous les imports sont termines ===")


if __name__ == "__main__":
    main()
