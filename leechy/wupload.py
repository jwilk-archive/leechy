# encoding=UTF-8

# Copyright © 2012 Jakub Wilk <jwilk@jwilk.net>
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

from leechy import Browser

import re
_delay_search = re.compile(r'var\s+countDownDelay\s*=\s*([0-9]+)').search
_tm_search = re.compile(
    r"id='tm' name='tm' value='([0-9]+)'.*"
    r"id='tm_hash' name='tm_hash' value='([0-9a-f]+)'",
    re.DOTALL
).search
_recaptcha_site_search = re.compile('Recaptcha[.]create[(]"([0-9A-Za-z_-]+)"').search
_recaptcha_challenge_search = re.compile('challenge : \'([0-9A-Za-z_-]+)\'').search
_download_now_search = re.compile('<a href="(http://s[0-9]+[.]wupload[.]com/download/[0-9a-f/]+)"><span>Download Now</span>').search
del re

import os
import random
import urllib
import urlparse

class Browser(Browser):

    pattern = r'^http://www.wupload.com/file/[0-9]+/'

    def download(self):
        main_uri = self.start_uri + '?start=1'
        _, _, target, _, _, _ = urlparse.urlparse(self.start_uri)
        ident, target = target.split('/')[-2:]
        if os.path.exists(target):
            self.log_info('Nothing to do.')
            return
        response = self.open(main_uri)
        content = response.read()
        while 1:
            match = _delay_search(content)
            if match is not None:
                [seconds] = match.groups()
                seconds = int(seconds)
                yield seconds
                match = _tm_search(content)
                if match is not None:
                    [tm, tm_hash] = match.groups()
                    data = urllib.urlencode(dict(
                        tm=tm,
                        tm_hash=tm_hash,
                    ))
                    response = self.open(main_uri, data)
                else:
                    response = self.open(main_uri)
                content = response.read()
                continue
            match = _recaptcha_site_search(content)
            if match is not None:
                [recaptcha_site_id] = match.groups()
                uri = 'http://www.google.com/recaptcha/api/challenge?' + urllib.urlencode(dict(
                    k=recaptcha_site_id,
                    ajax=1,
                    cachestop=random.random()
                ))
                response = self.open_novisit(uri)
                content = response.read()
                match = _recaptcha_challenge_search(content)
                if match is None:
                    self.report_api_error('recaptcha-challenge')
                [recaptcha_challenge_id] = match.groups()
                uri = 'http://www.google.com/recaptcha/api/image?' + urllib.urlencode(dict(
                    c=recaptcha_challenge_id
                ))
                captcha = self.open_novisit(uri)
                token = self.read_captcha(captcha)
                data = urllib.urlencode(dict(
                    recaptcha_challenge_field=recaptcha_challenge_id,
                    recaptcha_response_field=token,
                ))
                response = self.open(main_uri, data=data)
                content = response.read()
                continue
            break
        match = _download_now_search(content)
        if match is None:
            self.report_api_error('download-now')
        [uri] = match.groups()
        self.wget(uri, target)

# vim:ts=4 sw=4 et
