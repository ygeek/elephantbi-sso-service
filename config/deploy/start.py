#! /usr/bin/env python

from plumbum import cli, RETCODE
from plumbum.cmd import supervisord, uwsgi


class AppMain(cli.Application):

    def main(self, *args):
        if args:
            print("Unknown command {0!r}".format(args[0]))
            return 1  # error exit code
        if not self.nested_command:
            # will be ``None`` if no sub-command follows
            print("No command given")
            return 1  # error exit code


@AppMain.subcommand('server')
class AppServer(cli.Application):

    def main(self):
        return supervisord['-n', '-c', '/etc/supervisord.conf'
               ] & RETCODE(FG=True)


@AppMain.subcommand('reload')
class AppReload(cli.Application):

    def main(self):
        return uwsgi['--reload', '/tmp/uwsgi.pid'] & RETCODE(FG=True)


if __name__ == '__main__':
    AppMain.run()
