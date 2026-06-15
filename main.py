import argparse


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Sistema de Senhas (SAAS) - Modulos Distribuidos"
    )
    parser.add_argument(
        "modulo",
        choices=["srv", "ts", "ta", "tv"],
        help="Modulo a ser iniciado",
    )
    parser.add_argument(
        "--address",
        default="localhost:5000",
        help="Endereco do servidor SRV (default: localhost:5000)",
    )

    args = parser.parse_args()

    if args.modulo == "srv":
        from srv import run_srv
        run_srv(args.address)
    elif args.modulo == "ts":
        from ts import run_ts
        run_ts(args.address)
    elif args.modulo == "ta":
        from ta import run_ta
        run_ta(args.address)
    elif args.modulo == "tv":
        from tv import run_tv
        run_tv(args.address)


if __name__ == "__main__":
    main()
