from src.config import load_config
from src.dashboard.app import create_app


def main() -> None:
    config = load_config()
    app = create_app(config)
    app.run(
        host=config.dashboard_host,
        port=config.dashboard_port,
        debug=False,
    )


if __name__ == "__main__":
    main()
