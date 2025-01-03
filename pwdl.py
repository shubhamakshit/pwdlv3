import argparse

from mainLogic.startup.Login.call_login import LoginInterface
from mainLogic import downloader
from mainLogic.utils import glv_var


def parse_arguments():
    """Parse command-line arguments."""
    parser = argparse.ArgumentParser(description='PhysicsWallah M3u8 parser.')
    parser.add_argument('--csv-file', type=str, help='Input csv file. Legacy Support too.')
    parser.add_argument('--id', type=str,
                        help='PhysicsWallh Video Id for single usage. Incompatible with --csv-file. Must be used with --name')
    parser.add_argument('--name', type=str,
                        help='Name for the output file. Incompatible with --csv-file. Must be used with --id')
    parser.add_argument('--dir', type=str, help='Output Directory')
    parser.add_argument('--verbose', action='store_true', help='Verbose Output')
    parser.add_argument('--shell', action='store_true', help='Start the shell')
    parser.add_argument('--shell-i','-i',action='store_true', help='Start the interactive shell (v2)')
    parser.add_argument('--webui', nargs='?', const=-1, type=int, help='Start the Webui')
    parser.add_argument('--simulate', action='store_true',
                        help='Simulate the download process. No files will be downloaded. Incompatible wit h '
                             '--csv-file. Must be used with --id and --name')
    parser.add_argument('--version', action='version', version='%(prog)s 1.0')
    parser.add_argument('--login', action='store_true', help='Login to PhysicsWallah')
    parser.add_argument('--ignore-token', action='store_true', help='Ignore the token.')

    return parser.parse_args()


if __name__ == "__main__":
    args = parse_arguments()

    if args.login:
        LoginInterface.cli()
    if args.ignore_token:
        glv_var.vars['ig_token'] = True
    if args.shell_i:
        from beta.shellLogic.shell_var import app
        app.run()

    downloader.main(
        csv_file=args.csv_file,
        id=args.id,
        name=args.name,
        directory=args.dir,
        verbose=args.verbose,
        shell=args.shell,
        webui_port=args.webui,
        simulate=args.simulate
    )
