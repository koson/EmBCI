#!/usr/bin/env python
# coding=utf-8
#
# File: EmBCI/embci/webui/__init__.py
# Author: Hankso
# Webpage: http://github.com/hankso
# Time: Fri 14 Sep 2018 21:51:46 CST

'''Web-based User Interface of EmBCI'''

from __future__ import absolute_import

# requirements.txt: network: gevent
from gevent import monkey; monkey.patch_all(select=False, thread=False) # noqa
from gevent.pywsgi import WSGIServer

# built-in
import os
import sys
import logging
import functools
import importlib
import traceback
from logging.handlers import RotatingFileHandler

# requirements.txt: network: bottle, gevent, gevent-websocket
import bottle
from geventwebsocket.handler import WebSocketHandler

from ..utils import (
    argparse, config_logger, get_config, get_self_ip_addr, get_boolean,
    LockedFile, LoggerStream, AttributeDict, AttributeList
)
from ..configs import DIR_PID, DIR_LOG
from .. import version


# =============================================================================
# constants
#
__basedir__  = os.path.dirname(os.path.abspath(__file__))
__port__     = get_config('WEBUI_PORT', 80, type=int)
__host__     = get_self_ip_addr(get_config('WEBUI_HOST', '0.0.0.0'))
__index__    = os.path.join(__basedir__, 'index.html')
__pidfile__  = os.path.join(DIR_PID, 'webui.pid')
root         = bottle.Bottle()
logger       = logging.getLogger(__name__)
subapps      = AttributeList()
masked       = set()
LOGDIRS      = set([DIR_LOG, ])
SNIPDIRS     = set([os.path.join(__basedir__, 'snippets'), ])
DEFAULT_ICON = '/images/icon2.png'


# =============================================================================
# routes
#
@root.route('/')
def webui_root():
    bottle.redirect('/index.html')


@root.route('/index.html')
@bottle.view(__index__)
def webui_index():
    return webui_appinfo()


@root.route('/appinfo')
def webui_appinfo():
    if get_boolean(bottle.request.query.get('reload')):
        mount_apps()
    apps = []
    for app in subapps:
        if app.obj is None:
            continue
        appd = app.copy(dict)
        appd.pop('obj')
        apps.append(appd)
    return {'subapps': apps}


@root.route('/snippets/<filename:path>')
def webui_snippets(filename):
    for root in SNIPDIRS:
        if os.path.exists(os.path.join(root, filename)):
            return bottle.static_file(filename, root)
    bottle.abort(404, 'File does not exist.')


@root.route('/log/<filename:path>')
def webui_logfiles(filename):
    for root in LOGDIRS:
        if os.path.exists(os.path.join(root, filename)):
            return bottle.static_file(filename, root)
    bottle.abort(404, 'File does not exist.')


@root.route('/<filename:path>')
def webui_static(filename):
    return bottle.static_file(filename, root=__basedir__)


# =============================================================================
# functions
#
def mount_apps(applist=subapps):
    '''
    Mount subapps from:
    0. default settings of `applist`
    1. list of masked apps from commmand line (runtime)
    2. embci.apps.__all__
    3. application folders under `/path/to/embci/apps/`
    '''
    import embci.apps

    for appname in masked:
        if appname in applist.name:
            continue
        applist.append(AttributeDict(
            name=appname, obj=None, path='',
            loader='masked by embci.webui.__main__'
        ))

    for appname in embci.apps.__all__:
        try:
            appmod = getattr(embci.apps, appname)
            if appmod is None:  # This app has been masked
                continue
            apppath = os.path.abspath(appmod.__path__[0])
            if apppath in applist.path:  # Different app names of same path
                continue
            appname = getattr(appmod, 'APPNAME', appname)
            if appname in applist.name:  # Same app name of different paths
                continue
            appobj = appmod.application
        except AttributeError:
            logger.info('Load `application` object from app `{}` failed. '
                        'Check out `embci.apps.__doc__`.'.format(appname))
            if appname in applist.name:
                continue
            applist.append(AttributeDict(
                name=appname, obj=None, path='',
                loader='masked by embci.apps.__all__'
            ))
        else:
            applist.append(AttributeDict(
                name=appname, obj=appobj, path=apppath,
                loader='loaded by embci.apps.__all__',
                hidden=getattr(appmod, 'HIDDEN', False),
            ))

    for appfolder in os.listdir(embci.apps.__basedir__):
        if appfolder[0] in ['_', '.']:
            continue
        apppath = os.path.join(embci.apps.__basedir__, appfolder)  # abspath
        if not os.path.isdir(apppath):
            continue
        if apppath in applist.path:
            continue
        # If use `import {appname}` and `embci/apps/{appname}` can not be
        # successfully imported (lack of "__init__.py" for example), python
        # will then try to import {appname} from other paths in sys.path.
        # So here we use `importlib.import_module("embci.apps.{appname}")`
        try:
            appmod = importlib.import_module('embci.apps.' + appfolder)
            appname = getattr(appmod, 'APPNAME', appfolder)
            if appname in applist.name:
                continue
            appobj = appmod.application
        except (ImportError, AttributeError):
            pass
        except Exception:
            logger.info('Load app `{}` failed!'.format(appname))
            logger.error(traceback.format_exc())
        else:
            applist.append(AttributeDict(
                name=appname, obj=appobj, path=apppath,
                loader='loaded by embci.apps.__basedir__',
                hidden=getattr(appmod, 'HIDDEN', False),
            ))

    for app in applist:
        if app.obj is None:  # skip masked apps
            continue
        app.target = '/apps/' + app.name.lower()
        root.mount(app.target, app.obj)
        logger.debug('link `{target}` to `{name}`'.format(**app))
        app.icon = os.path.join(app.path, 'icon.png')
        if not os.path.exists(app.icon):
            app.icon = DEFAULT_ICON
        snippets = os.path.join(app.path, 'snippets')
        if os.path.exists(snippets):
            app.snippets = snippets
            SNIPDIRS.add(snippets)
    return applist


class GeventWebsocketServer(bottle.ServerAdapter):
    '''Gevent websocket server using local logger.'''
    def run(self, app):
        _logger = self.options.get('logger', logger)
        server = WSGIServer(
            listener=(self.host, self.port),
            application=app,
            # Fix WebSocketHandler log_request, see more below:
            #  log=LoggerStream(_logger, logging.DEBUG),
            error_log=LoggerStream(_logger, logging.ERROR),
            handler_class=WebSocketHandler)
        # WebSocketHandler use `server.logger.info`
        # instead of `server.log.debug`
        server.logger = _logger
        server.serve_forever()


def serve_forever(host, port, app=root, **k):
    try:
        bottle.run(app, GeventWebsocketServer, host, port, quiet=True, **k)
    except KeyboardInterrupt:
        pass
    except Exception:
        logger.error(traceback.format_exc())


def make_parser():
    parser = argparse.ArgumentParser(prog=__name__, description=(
        'Network based user interface of EmBCI embedded system. '
        'Default listen on http://{}:{}. '
        'Address can be specified by user.').format(__host__, __port__))
    parser.add_argument('--host', default=__host__, type=str, help='hostname')
    parser.add_argument('--port', default=__port__, type=int, help='port num')
    parser.add_argument('--exclude', nargs='*', help='subapp names to skip')
    parser.add_argument(
        '-v', '--verbose', default=0, action='count',
        help='output more information, -vv for deeper details')
    parser.add_argument(
        '-l', '--log', type=str, dest='logfile',
        help='log output to a file instead of stdout')
    parser.add_argument(
        '-p', '--pid', default=__pidfile__, dest='pidfile',
        help='pid file used for EmBCI WebUI, default `%s`' % __pidfile__)
    parser.add_argument(
        '--newtab', default=True, type=get_boolean,
        help='boolean, whether to open webpage of WebUI in browser')
    parser.add_argument('-V', '--version', action='version', version=version())
    return parser


def open_webpage(addr):
    '''open embci-webui page if not run by root user'''
    if os.getuid() == 0:
        return
    try:
        from webbrowser import open_new_tab
        open_new_tab(addr)
    except Exception:
        pass


def main(arg):
    global __host__, __port__, __pidfile__
    parser = make_parser()
    args = parser.parse_args(arg)

    # ensure host address legal
    from socket import inet_aton, inet_ntoa, error
    try:
        __host__ = args.host.replace('localhost', '127.0.0.1')
        __host__ = inet_ntoa(inet_aton(__host__))
        __port__ = args.port
    except error:
        parser.error("argument --host: invalid address: '%s'" % args.host)

    # config logger with loglevel by counting number of -v
    level = max(logging.WARN - args.verbose * 10, 10)
    if args.logfile is not None:
        LOGDIRS.add(os.path.dirname(os.path.abspath(args.logfile)))
        kwargs = {
            'filename': args.logfile,
            'handler': functools.partial(
                RotatingFileHandler, maxBytes=100 * 2**10, backupCount=5)
        }
    else:
        kwargs = {'stream': sys.stdout}
    config_logger(logger, level, **kwargs)

    # mask apps from command line
    masked.update(args.exclude or [])
    mount_apps(subapps)

    __pidfile__ = args.pidfile
    pidfile = LockedFile(__pidfile__, pidfile=True)
    pidfile.acquire()

    addr = 'http://%s:%d/' % (args.host, args.port)
    logger.info('Listening on : ' + addr)
    logger.info('Hit Ctrl-C to quit.\n')
    if args.newtab:
        open_webpage(addr)

    logger.info('Using PIDFILE: {}'.format(pidfile))
    serve_forever(__host__, __port__, logger=logger)
    pidfile.release()
