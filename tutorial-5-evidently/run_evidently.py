#!/usr/bin/env python3
"""Start Evidently AI service with SQL storage support.

The `evidently ui` CLI doesn't auto-import the SQL storage components,
so the `database` config section is unrecognized. This wrapper imports
the SQL module first, then starts the service using the same code path.
"""

# Import SQL components BEFORE loading config - this registers
# the `database` section in SECTION_COMPONENT_TYPE_MAPPING
import evidently.ui.service.storage.sql.components  # noqa: F401

from evidently.ui.service.app import get_config, run


def main():
    import argparse

    parser = argparse.ArgumentParser(description="Run Evidently UI with SQL support")
    parser.add_argument("--host", default="0.0.0.0")
    parser.add_argument("--port", type=int, default=8000)
    parser.add_argument("--workspace", default="workspace")
    parser.add_argument("--conf-path", default=None)
    args = parser.parse_args()

    config = get_config(
        host=args.host,
        port=args.port,
        workspace=args.workspace,
        conf_path=args.conf_path,
    )
    run(config)


if __name__ == "__main__":
    main()
