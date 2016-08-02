#!/usr/bin/env python
"""
script to iterate through vassal configs containing
an extra section called [vassaldeployer] as well as the
initial [uwsgi] config and link the uwsgi app up
in the master nginx config file

Eg:

[uwsgi]
home=/opt/app
socket=127.0.0.1:3030
module=some_package.some_module:APP
master=1
enable-threads=true
workers=2
die-on-term=1
virtualenv=/opt/app/venv

[vassaldeployer]
app_url=/some_package
python=python2.7
requirements=some_package=0.1.2.some_dep==1.2.3
pip_options= --extra-index=mypypi:8080

This script will create the virtualenv in the location specified,
install the requirements via pip and add a section to
the master nginx conf mapping /some_package to the uwsgi app
listening on the specified socket

"""
import os
import argparse
import subprocess


try:
    import ConfigParser as configparser
except ImportError:
    import configparser


def build_parser():
    parser = argparse.ArgumentParser(
        description='uwsgi vassal config processor that builds nginx confs'
    )
    parser.add_argument(
        '--vassals',
        help='directory to write vassals configs',
        required=True,
        dest='vassals_out'
    )
    parser.add_argument(
        '--input-vassals', '-i',
        help='directory containing vassals configs with extra deployer conf section',
        required=True,
        dest='vassals_in'
    )
    parser.add_argument(
        '--sites-enabled',
        help='nginx sites-enabled directory location',
        default='/etc/nginx/sites-enabled',
        dest='sites_enabled'
    )
    parser.add_argument(
        '--sites-available',
        help='nginx sites-available directory location',
        default='/etc/nginx/sites-available',
        dest='sites_available'
    )
    parser.add_argument(
        '--nginx-port',
        help='nginx server port number',
        default=8080,
        dest='nginx_port'
        )
    parser.add_argument(
        '--nginx-site',
        help='nginx site name',
        default='uwsgi_vassals',
        dest='nginx_site'
        )

    opts = parser.parse_args()
    return opts


def list_vassals_configs(directory):
    result = []
    for f in os.listdir(directory):
        if f.endswith('.ini'):
            result.append(
                os.path.join(directory, f)
            )
    return result


class VassalConfig(dict):
    """
    container for uwsgi config
    """
    SECTION = 'vassaldeployer'

    def __init__(self, conf_file):
        self.config_file = conf_file
        self.basename = os.path.basename(self.config_file)

    def load(self):
        """
        read the ini file
        """
        self.parser = configparser.RawConfigParser()
        self.parser.read(self.config_file)
        for section in self.parser.sections():
            self.setdefault(section, {})
            for option in self.parser.options(section):
                self[section].setdefault(
                    option,
                    self.parser.get(section, option)
                )

    def uwsgi_config(self, **settings):
        """
        write the cleaned uwsgi config including
        additional settings
        """
        content = "[uwsgi]\n"
        values = dict(self['uwsgi'])
        values.update(settings)
        content += '\n'.join("{}={}".format(k, v) for k, v in values.iteritems())
        return content

    def nginx_config(self):
        """
        make the location section of the nginx conf

        routing the apps based off a subdomain of the nginx
        server requires the two extra params:
          SCRIPT_NAME tells nginx to strip the url
          uwsgi_modifier1 30 is the magic that makes it work
          see: http://blog.codepainters.com/2012/08/05/wsgi-deployment-under-a-subpath-using-uwsgi-and-nginx/
          for more details.

        """
        conf = "location {}".format(self.app_url)
        conf += "{\n"
        conf += "    include uwsgi_params;\n"
        conf += "    uwsgi_pass 127.0.0.1:{};\n".format(self.uwsgi_port)
        conf += "    uwsgi_param SCRIPT_NAME {};\n".format(self.app_url)
        conf += "    uwsgi_modifier1 30;\n"
        conf += "}\n"
        return conf

    @property
    def uwsgi_socket(self):
        return self['uwsgi']['socket']

    @property
    def uwsgi_home(self):
        return self['uwsgi']['home']

    @property
    def uwsgi_virtualenv(self):
        if not self['uwsgi'].get('virtualenv'):
            venv = os.path.join(self.uwsgi_home, 'venv')
            self['uwsgi']['virtualenv'] = venv
        return self['uwsgi']['virtualenv']

    @property
    def uwsgi_port(self):
        return self.uwsgi_socket.split(':', 1)[1]

    @property
    def section(self):
        return self[self.SECTION]

    @property
    def app_url(self):
        return self.section.get('app_url')

    @property
    def app_python(self):
        return self.section.get('python')

    @property
    def app_requirements(self):
        return self.section.get('requirements')

    @property
    def pip_options(self):
        return self.section.get('pip_options', '')

    def make_virtualenv(self):
        """
        execute the virtualenv command
        """
        cmd = [
            "virtualenv", "-p",
            "{}".format(self.app_python),
            self.uwsgi_virtualenv
        ]
        subprocess.check_output(cmd, stderr=subprocess.STDOUT)

    def pip_install(self):
        reqs = ' '.join([
            x.strip()
            for x in self.app_requirements.split(',') if x.strip
            ]
        )
        cmd = (
            " . {}/bin/activate && "
            "pip install {} {}"
        ).format(self.uwsgi_virtualenv, self.pip_options, reqs)
        subprocess.check_output(cmd, stderr=subprocess.STDOUT, shell=True)

    def write(self, dirname):
        f = os.path.join(dirname, self.basename)
        with open(f, 'w') as handle:
            handle.write(self.uwsgi_config())


def main():
    opts = build_parser()
    nginx_conf = (
        "server {{\n"
        "    listen {};\n"
        "    server_tokens off;\n"
        "    server_name {};\n\n"
    ).format(opts.nginx_port, opts.nginx_site)

    for vassal in list_vassals_configs(opts.vassals_in):
        vassal_conf = VassalConfig(vassal)
        vassal_conf.load()
        vassal_conf.make_virtualenv()
        vassal_conf.pip_install()
        vassal_conf.write(opts.vassals_out)
        nginx_conf += vassal_conf.nginx_config()

    nginx_conf += "\n}\n"
    nginx_conf_file = "{}.conf".format(opts.nginx_site)
    avail_file = os.path.join(opts.sites_available, nginx_conf_file)
    with open(avail_file, 'w') as handle:
        handle.write(nginx_conf)

    enabled_file = os.path.join(opts.sites_enabled, nginx_conf_file)
    # symlink available => enabled
    os.system("ln -sf {} {}".format(avail_file, enabled_file))


if __name__ == '__main__':
    main()