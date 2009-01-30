# encoding=UTF-8

# Copyright © 2009 Jakub Wilk <ubanus@users.sf.net>
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; version 2 dated June, 1991.
#
# This program is distributed in the hope that it will be useful, but
# WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
# General Public License for more details.

import mechanize

_dispatch = []

def register_plugin(browser):
    import re
    match = re.compile(browser.pattern).match
    _dispatch.append((match, browser))
    
def register_all_plugins():
    import pkgutil
    _dispatch[:] = []
    for importer, name, ispkg in pkgutil.iter_modules(__path__):
        thismodule = __import__('', globals=globals(), fromlist=(name,), level=1)
        try:
            browser = getattr(thismodule, name).Browser
        except AttributeError:
            continue
        else:
            register_plugin(browser)

def dispatch(uri, **kwargs):
    for match, browser_class in _dispatch:
        if match(uri):
            return browser_class(uri, **kwargs).download()
    raise NoMatchingPlugin

def _ioctl_GWINSZ(fp):
    import fcntl
    import termios
    import struct
    y, x = struct.unpack('hh', fcntl.ioctl(fp, termios.TIOCGWINSZ, '\0' * 4))
    return x, y

def _get_terminal_size(fp):
    try:
        return _ioctl_GWINSZ(fp.fileno())
    except:
        pass
    try:
        import os
        return tuple(int(os.getenv(x)) for x in ('COLUMNS', 'LINES'))
    except:
        return (80, 25)

def _read_token():
    return raw_input('Enter token: ')

class Progress(object):

    def __init__(self, fp, max):
        self.max = max
        if fp.isatty():
            self.fp = fp
            self.width, _ = _get_terminal_size(fp)
            self.width -= 4
            if self.width < 8:
                self.fp = None
                self.width = None
        else:
            self.fp = None
            self.width = None
        self.n = -1
        self.update(0)
    
    def update(self, n):
        if self.fp is not None and n > self.n:
            b = self.width * n // self.max
            a = self.width - b
            status = ''.join(('=' * (b - 1), '>' * (b > 0), ' ' * a))
            self.fp.write('\r[%s]' % status)
            if n >= self.max:
                self.fp.write('\n')
            self.fp.flush()
        self.n = n

class NoMatchingPlugin(Exception):
    pass

class SimultaneousDownload(Exception):
    pass

class ApiError(Exception):

    def __init__(self, ua, code=None):
        import os
        import tempfile
        Exception.__init__(self, ua)
        self.code = code
        content = ua.response().read()
        fd, self.dump_name = tempfile.mkstemp(prefix='leechy-', suffix='.html')
        fp = os.fdopen(fd, 'wb')
        try:
            fp.write(content)
        finally:
            fp.close()

def sleep(n):
    import sys
    import time
    log_info('Waiting %d seconds...' % n)
    progress = Progress(sys.stderr, n)
    for i in xrange(n):
        progress.update(i)
        time.sleep(1)
    progress.update(n)

class WgetFailure(Exception):
    pass

def wget(uri, target):
    import subprocess
    import os
    tmp_target = '%s.leechy-tmp' % target
    rc = subprocess.call(['wget', '-O', tmp_target, '--', uri])
    if rc != 0:
        raise WgetFailure()
    os.rename(tmp_target, target)

def log_info(message):
    import sys
    print >>sys.stderr, message

def log_error(message):
    import sys
    print >>sys.stderr, message

def html_unescape(html):
    if '<' in html:
        raise ValueError
    from xml.etree import cElementTree as ET
    return ET.fromstring('<root>%s</root>' % html).text

class Browser(mechanize.Browser):

    pattern = None

    def download(self, uri):
        raise NotImplementedError

    def __init__(self, start_uri, debug=0):
        import locale
        mechanize.Browser.__init__(self)
        self.start_uri = start_uri
        self.addheaders = [('User-Agent', 'Mozilla/5.0')]
        self.set_handle_robots(0)
        self.filename_encoding = locale.getpreferredencoding()
        if debug:
            self.set_debug_http(1)

    def api_error(self, code=None):
        raise ApiError(self, code)

    def simultaneous_download(self):
        raise SimultaneousDownload(self)

    def solve_captacha(self, image):
        return None

    def read_captcha(self, image_fp):
        import sys
        try:
            import Image, ImageChops
            image = Image.open(image_fp)
            result = self.solve_captcha(image)
            if result is not None:
                return result
            terminal_width, terminal_height = _get_terminal_size(sys.stdout)
            if terminal_width >= 40 and terminal_height >= 25:
                image.convert('L')
                bg = Image.new('L', image.size, 0)
                diff = ImageChops.difference(image, bg)
                bbox = diff.getbbox()
                if bbox:
                    image = image.crop(bbox)
                width, height = image.size
                new_width = terminal_width - 2
                new_height = int(1.0 * height / width * new_width)
                if new_height + 8 > terminal_height:
                    new_height = terminal_height - 8
                    new_width = int(1.0 * width / height * new_height)
                image = image.resize((new_width, new_height))
                for y in xrange(new_height):
                    for x in xrange(new_width):
                        sys.stdout.write('#' if image.getpixel((x, y)) >  0 else ' ')
                    sys.stdout.write('\n')
            return _read_token()
        except ImportError:
            pass
        import tempfile
        import os
        fp = tempfile.NamedTemporaryFile(prefix='leechy-', suffix='.gif')
        try:
            try:
                fp.write(http_fp.read())
            finally:
                fp.close()
            print 'Token image path:', fp.name
            return _read_token()
        finally:
            os.unlink(fp.name)


    log_info = staticmethod(log_info)
    log_error = staticmethod(log_error)

    wget = staticmethod(wget)
    sleep = staticmethod(sleep)
    html_unescape = staticmethod(html_unescape)

# vim:ts=4 sw=4 et
