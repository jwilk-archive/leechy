# encoding=UTF-8

# Copyright © 2009, 2010, 2012 Jakub Wilk <jwilk@jwilk.net>
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

import re
_target_search = re.compile('<div class="dl_first_filename">\s+([^<]+)').search
_click_link_re = re.compile('captcha=1')
_wait1_search = re.compile(r'<script type="text/javascript">countdown[(](\d+),').search
_captcha_search = re.compile('<img style="[^"]+" src="(share/includes/captcha.php[?]t=\d+)"').search
_uri_search = re.compile('<a class="Orange_Link" href="(http://[0-9.]+/[0-9a-f]+)"').search
_next_file_s = 'You could download your next file'
_limit_reached_s = 'Limit reached!'
_bad_captcha_s = 'You may forgot the security code or it might be wrong'
del re

import os
import shutil
import subprocess as ipc
import tempfile
from leechy import Browser

class Browser(Browser):

    pattern = r'^http://(?:www[.])?netload[.]in/[0-9a-zA-Z]+(/|[.]htm$)'

    def enhance_captcha(self, image):
        try:
            from PIL import ImageFilter
        except ImportError:
            return image
        return image.convert('L').filter(ImageFilter.MedianFilter(size=3))

    def solve_captcha(self, image):
        tmpdir = tempfile.mkdtemp()
        try:
            image_filename = os.path.join(tmpdir, 'image.tif')
            image.save(image_filename)
            config_filename = os.path.join(tmpdir, 'config')
            with open(config_filename, 'wt') as config:
                config.write('tessedit_char_whitelist 0123456789')
            result_prefix = os.path.join(tmpdir, 'result')
            try:
                ipc.check_call(['tesseract', image_filename, result_prefix, 'batch', config_filename])
            except OSError:
                return
            with open(result_prefix + '.txt') as file:
                result = file.read().strip()
            if len(result) == 4 and result.isdigit():
                return result
            return
        finally:
            shutil.rmtree(tmpdir)

    def download(self):
        while True:
            response = self.open(self.start_uri)
            content = response.read()
            target_match = _target_search(content)
            if target_match is None:
                self.report_api_error('target')
            target = target_match.group(1)
            if target.endswith('..'):
                # Oops, filename was truncated. Recover it from URL.
                target = self.start_uri.rsplit('/', 1)[-1]
                if target.endswith('.htm'):
                    target = target[:-4]
            if os.path.exists(target):
                self.log_info('Nothing to do.')
                return
            response = self.follow_link(url_regex=_click_link_re)
            content = response.read()
            sleep_match = _wait1_search(content)
            if sleep_match is None:
                self.report_api_error('sleep1')
            seconds = (int(sleep_match.group(1)) + 99) // 100
            captcha_match = _captcha_search(content)
            if captcha_match is None:
                self.report_api_error()
            captcha_uri = '/' + captcha_match.group(1)
            captcha = self.open_novisit(captcha_uri)
            token = self.read_captcha(captcha)
            yield seconds
            self.select_form(nr=0)
            self['captcha_check'] = token
            response = self.submit()
            content = response.read()
            sleep_match = _wait1_search(content)
            if sleep_match is None:
                if _bad_captcha_s in content:
                    continue
                self.report_api_error('sleep2')
            seconds = (int(sleep_match.group(1)) + 99) // 100
            uri_match = _uri_search(content)
            if uri_match is None:
                if _next_file_s in content:
                    yield seconds
                    continue
                if _limit_reached_s in content:
                    yield 3600
                    continue
                self.report_api_error('uri')
            uri = uri_match.group(1)
            yield seconds
            self.wget(uri, target)
            return

# vim:ts=4 sts=4 sw=4 et
