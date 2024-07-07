import argparse
from mainLogic import downloader

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
    parser.add_argument('--webui', nargs='?', const=-1, type=int, help='Start the Webui')
    parser.add_argument('--simulate', action='store_true',
                        help='Simulate the download process. No files will be downloaded. Incompatible wit h --csv-file. Must be used with --id and --name')
    return parser.parse_args()

if __name__ == "__main__":
    args = parse_arguments()
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
