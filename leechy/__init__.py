# encoding=UTF-8

# Copyright © 2009, 2010 Jakub Wilk <jwilk@jwilk.net>
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the “Software”), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED “AS IS”, WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

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
        if not match(uri):
            continue
        for n in browser_class(uri, **kwargs).download():
            sleep(n)
        return
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
    except Exception:
        pass
    try:
        import os
        return tuple(int(os.getenv(x)) for x in ('COLUMNS', 'LINES'))
    except Exception:
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

class TemporaryFailure(Exception):
    pass

class SimultaneousDownload(Exception):
    pass

class FileNotFound(Exception):
    pass

class ApiError(Exception):

    def __init__(self, ua, code=None, dump=False):
        import os
        import tempfile
        Exception.__init__(self, ua)
        self.code = code
        content = ua.response().read()
        if dump:
            fd, self.dump_name = tempfile.mkstemp(prefix='leechy-', suffix='.html')
            fp = os.fdopen(fd, 'wb')
            try:
                fp.write(content)
            finally:
                fp.close()
        else:
            self.dump_name = None

def sleep(n):
    import sys
    import time
    if n == 0:
        return
    log_info('Waiting %d seconds...' % n)
    progress = Progress(sys.stderr, n)
    for i in xrange(n):
        progress.update(i)
        time.sleep(1)
    progress.update(n)

class WgetFailure(Exception):
    pass

def wget(uri, target, data=None):
    import subprocess
    import os
    tmp_target = '%s.leechy-tmp' % target
    args = ['wget', '-O', tmp_target, '--', uri]
    if data is not None:
        args[1:1] = ['--post-data', data]
    rc = subprocess.call(args)
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
        self.debug = debug
        if debug:
            self.set_debug_http(1)

    def report_api_error(self, code=None):
        raise ApiError(self, code, dump=self.debug)

    def report_simultaneous_download(self):
        raise SimultaneousDownload(self)

    def report_file_not_found(self):
        raise FileNotFound(self)

    def report_temporary_failure(self):
        raise TemporaryFailure(self)

    def solve_captcha(self, image):
        return None

    def enhance_captcha(self, image):
        return image

    def read_captcha(self, image_fp):
        import sys
        try:
            import aalib
        except ImportError:
            aalib = None
        try:
            import Image, ImageChops
            image = Image.open(image_fp)
            image = self.enhance_captcha(image)
            result = self.solve_captcha(image)
            if result is not None:
                return result
            terminal_width, terminal_height = _get_terminal_size(sys.stdout)
            if terminal_width >= 40 and terminal_height >= 25:
                image = image.convert('L')
                image = ImageChops.invert(image)
                bg = Image.new('L', image.size, 255)
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
                if aalib:
                    screen = aalib.AnsiScreen(width=new_width, height=new_height)
                    image = image.resize(screen.virtual_size)
                    screen.put_image((0, 0), image)
                    text = screen.render()
                    sys.stdout.write(text)
                    sys.stdout.write('\n')
                else:
                    width, height = new_width, new_height
                    image = image.resize((width, height))
                    for y in xrange(height):
                        for x in xrange(width):
                            sys.stdout.write('#' if image.getpixel((x, y)) > 0 else ' ')
                        sys.stdout.write('\n')
            return _read_token()
        except ImportError:
            pass
        import tempfile
        fp = tempfile.NamedTemporaryFile(prefix='leechy-', suffix='.gif')
        try:
            fp.write(image_fp.read())
            fp.flush()
            print 'Token image path:', fp.name
            return _read_token()
        finally:
            fp.close()


    log_info = staticmethod(log_info)
    log_error = staticmethod(log_error)

    wget = staticmethod(wget)
    html_unescape = staticmethod(html_unescape)

# vim:ts=4 sw=4 et
