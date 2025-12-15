import argparse

from mainLogic.startup.Login.call_login import LoginInterface
from mainLogic import downloader
from mainLogic.utils import glv_var
from mainLogic.utils.Debugger import Debugger
from mainLogic.utils.glv_var import debugger


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
    parser.add_argument("--command",default="",help="Command to execute in shell")
    parser.add_argument('--shell-i','-i',action='store_true', help='Start the interactive shell (v2)')
    parser.add_argument('--tmp-dir', type=str, help='Temporary Directory')
    parser.add_argument('--webui', nargs='?', const=-1, type=int, help='Start the Webui')
    parser.add_argument('--no-reloader', action='store_true', help='Disable the Flask reloader in debug mode')
    parser.add_argument('--ssl', action='store_true', help='Enable HTTPS/SSL for the webui')
    parser.add_argument('--ssl-cert', type=str, help='Path to SSL certificate file (cert.pem)')
    parser.add_argument('--ssl-key', type=str, help='Path to SSL private key file (key.pem)')
    parser.add_argument('--ssl-password', type=str, help='Password for SSL private key (if encrypted)')
    parser.add_argument('--simulate', action='store_true',
                        help='Simulate the download process. No files will be downloaded. Incompatible wit h '
                             '--csv-file. Must be used with --id and --name')
    parser.add_argument('--version', action='version', version='%(prog)s 1.0')
    parser.add_argument('--login', action='store_true', help='Login to PhysicsWallah')
    parser.add_argument('--phone', type=str, help='Phone number for login (optional)')


    parser.add_argument('--ignore-token', action='store_true', help='Ignore the token.')
    parser.add_argument('--no-sync', action='store_true', help='Do not sync the token.')
    parser.add_argument("--new-dl","-L",action='store_true',help="New Downloader")
    parser.add_argument("--batch-name","-B",type=str,help="Batch Id")
    parser.add_argument("--topic-name","-T",type=str,help="Topic name ")
    parser.add_argument("--lecture-url","-U",type=str,help="Lecture URL")


    return parser.parse_args()


if __name__ == "__main__":
    args = parse_arguments()

    if args.login:
        LoginInterface.cli()
    elif args.phone:
        LoginInterface.cli(args.phone)

    if args.command:
        from beta.shellLogic import logic
        command = args.command.split()[0]
        args = args.command.split()[1:]
        logic.execute(
            command,
            args
        )
        exit(0)

    if args.ignore_token:
        glv_var.vars['ig_token'] = True
    if args.shell_i:
        from beta.shellLogic.shell_var import app
        app.run()

    try:
        from beta.Syncer.main import Syncer
        if not args.no_sync or not os.environ.get("PWDL_NO_SYNC"):
            sync = Syncer()
    except Exception as e:
        debugger.error(f"Error in Syncer: {e}")
        pass

    try:
        from auto_updater import run_auto_update
        run_auto_update(
            run_post_install_script_force=False,
            force_update=False
        )
    except Exception as e:
        debugger.error("Faild to update ")
        debugger.error(e)

    downloader.main(
        csv_file=args.csv_file,
        id=args.id,
        name=args.name,
        batch_name=args.batch_name,
        topic_name=args.topic_name,
        lecture_url=args.lecture_url,
        directory=args.dir,
        tmp_dir=args.tmp_dir,
        verbose=args.verbose,
        shell=args.shell,
        webui_port=args.webui,
        no_reloader=args.no_reloader,
        simulate=args.simulate,
        ssl=args.ssl,
        ssl_cert=args.ssl_cert,
        ssl_key=args.ssl_key,
        ssl_password=args.ssl_password
    )
