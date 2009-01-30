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

import re
_captcha_search = re.compile(r'<img src="(/capgen.php[?][0-9a-f]+)">').search
_wait_search = re.compile(r'^\s*x\d+=(\d+);', re.MULTILINE).search
_code_v1_search = re.compile(r'^\s*var ([a-z]) = String[.]fromCharCode[(]Math[.]abs[(]-([0-9]+)[)][)];', re.MULTILINE).search;
_code_v2_search = re.compile(r"^\s*var ([a-z]) = '([0-9a-f])' [+] String[.]fromCharCode[(]Math[.]sqrt[(](\d+)[)][)];", re.MULTILINE).search;
_uri_search = re.compile(r'"(http://www\d+[.]megaupload[.]com/files/[0-9a-f]+)\' [+] ([a-z]) [+] ([a-z]) [+] \'([0-9a-f]+/)([^/"]+)"').search;
del re

_captcha_letter_size = 25
_captcha_alphabet = \
{'A': [0, 0, 0, 31744, 64512, 64512, 65024, 126464, 118272, 118528, 116480, 247552, 231296, 230272, 493440, 524224, 524224, 524224, 983520, 917728, 917728, 917744, 0, 0, 0],
 'B': [0, 0, 65504, 262112, 524256, 508384, 458976, 458976, 458976, 229600, 262112, 65504, 262112, 508384, 393440, 393440, 393440, 393440, 459232, 524256, 524256, 262112, 0, 0, 0],
 'C': [0, 0, 0, 130048, 261888, 524160, 1017728, 918464, 917952, 262624, 224, 224, 224, 224, 224, 224, 393440, 917984, 984000, 1034176, 524160, 261632, 0, 0, 0],
 'D': [0, 0, 0, 32736, 131040, 262112, 516320, 1016032, 983264, 917728, 786656, 786656, 786656, 786656, 786656, 786656, 917728, 917728, 983264, 491744, 524256, 262112, 0, 0, 0],
 'E': [0, 0, 524224, 524224, 524224, 524224, 960, 960, 960, 65472, 65472, 65472, 65472, 960, 960, 960, 960, 960, 960, 524224, 524224, 524224, 0, 0, 0],
 'F': [0, 0, 0, 262016, 262016, 262016, 896, 896, 896, 896, 896, 896, 32640, 32640, 32640, 896, 896, 896, 896, 896, 896, 960, 0, 0, 0],
 'G': [0, 0, 0, 130560, 524160, 524224, 984032, 917728, 240, 112, 112, 112, 112, 1032304, 1032304, 1032304, 917616, 917744, 983520, 1042400, 982976, 982912, 0, 0, 0],
 'H': [0, 0, 917984, 917984, 917984, 917984, 917984, 917984, 917984, 917984, 1048544, 1048544, 1048544, 1048544, 917984, 917984, 917984, 917984, 917984, 917984, 917984, 917984, 0, 0, 0],
 'I': [0, 0, 14336, 14336, 14336, 14336, 14336, 14336, 14336, 14336, 14336, 14336, 14336, 14336, 14336, 14336, 14336, 14336, 14336, 14336, 14336, 14336, 0, 0, 0],
 'J': [0, 0, 0, 98304, 98304, 98304, 98304, 98304, 98304, 98304, 98304, 98304, 98304, 98304, 98304, 98304, 98304, 98304, 98304, 115456, 130816, 130560, 0, 0, 0],
 'K': [0, 0, 458976, 491744, 245984, 114912, 57568, 61664, 30944, 15584, 15584, 32736, 32736, 63456, 123872, 115168, 246240, 229600, 491744, 983520, 917984, 917984, 0, 0, 0],
 'L': [0, 0, 896, 896, 896, 896, 896, 896, 896, 896, 896, 896, 896, 896, 896, 896, 896, 896, 1920, 130944, 130944, 130944, 0, 0, 0],
 'M': [0, 0, 0, 2081272, 2081272, 1950648, 1950648, 1885112, 1884984, 1884984, 1894200, 1894200, 1894200, 1893944, 1863224, 1863224, 1867320, 1867320, 1866808, 1866808, 1866808, 1850424, 0, 0, 0],
 'N': [0, 0, 917744, 918000, 918512, 918512, 919536, 919536, 921328, 925424, 924912, 933104, 932080, 946416, 979184, 975088, 1040624, 1032432, 1016048, 1016048, 983280, 983280, 0, 0, 0],
 'O': [0, 0, 0, 31744, 130816, 524160, 1036224, 983520, 917984, 786656, 786672, 786544, 786544, 786544, 786544, 786672, 786656, 786656, 917984, 984000, 524224, 262016, 0, 0, 0],
 'P': [0, 0, 16352, 262112, 524256, 1048544, 917984, 917984, 917984, 917984, 983520, 1048544, 524256, 131040, 16352, 480, 480, 480, 480, 480, 480, 480, 0, 0, 0],
 'Q': [12288, 130560, 524160, 1048512, 984000, 1966560, 1835232, 1835232, 1835232, 1835248, 1835248, 1835248, 1835232, 1835232, 1835232, 1966560, 984000, 1048512, 524160, 261632, 30720, 28672, 28672, 61440, 1040384],
 'R': [0, 0, 32736, 262112, 524256, 508384, 458976, 393440, 393440, 393440, 458976, 524256, 524256, 131040, 115168, 245984, 229600, 229600, 458976, 459232, 459232, 393696, 0, 0, 0],
 'S': [0, 0, 0, 65024, 130944, 262016, 492480, 197056, 448, 448, 1920, 16256, 130560, 260096, 507904, 458752, 393216, 393664, 459232, 493504, 524160, 261888, 0, 0, 0],
 'T': [0, 0, 0, 524224, 524224, 524224, 61888, 28672, 28672, 28672, 28672, 28672, 28672, 28672, 28672, 28672, 28672, 28672, 28672, 28672, 61440, 61440, 0, 0, 0],
 'U': [0, 0, 0, 393440, 393440, 393440, 393440, 393440, 393440, 393440, 393440, 393440, 393440, 393440, 393440, 393440, 393696, 393696, 459200, 492480, 524224, 262016, 0, 0, 0],
 'V': [0, 0, 0, 786912, 917952, 917952, 918464, 918400, 459648, 460672, 460544, 493312, 231168, 232960, 232960, 249344, 122368, 130048, 130048, 64512, 63488, 63488, 0, 0, 0],
 'W': [0, 0, 3160092, 3177500, 3177500, 3177500, 3177532, 3731000, 3731000, 3720760, 3720760, 1885808, 1951600, 1951600, 2065392, 1016800, 1016800, 1016800, 983520, 983520, 459200, 459200, 0, 0, 0],
 'X': [0, 0, 0, 918400, 919424, 984832, 462592, 232960, 252928, 130048, 63488, 63488, 28672, 63488, 64512, 130048, 118272, 233216, 231168, 459648, 984000, 917952, 0, 0, 0],
 'Y': [0, 0, 0, 197568, 230272, 230272, 247552, 116480, 126720, 65024, 65024, 31744, 31744, 14336, 14336, 14336, 14336, 14336, 14336, 14336, 14336, 15360, 0, 0, 0],
 'Z': [0, 0, 0, 524160, 524160, 524160, 458752, 458752, 491520, 245760, 122880, 57344, 61440, 30720, 15360, 7680, 3584, 1792, 1920, 960, 524224, 524256, 0, 0, 0]}

def _expand_captcha_alphabet(alphabet, letter_size):
    for k, v in alphabet.iteritems():
        v = [''.join('#' if (1 << i) & line else ' ' for i in xrange(letter_size)) for line in v]
        yield k, v

_captcha_alphabet = dict(_expand_captcha_alphabet(_captcha_alphabet, _captcha_letter_size))
del _expand_captcha_alphabet

from leechy import Browser

class Browser(Browser):

    pattern = r'^http://(www[.])?megaupload[.]com(/[a-z]+)?/[?]d=[A-Z0-9]+$'


    def _find_letter(self, this):
        import itertools
        best = None
        best_n = 9999
        for ascii, that in _captcha_alphabet.iteritems():
            n = 0
            for this_line, that_line in itertools.izip(this, that):
                for this_pixel, that_pixel in itertools.izip(this_line, that_line):
                    if this_pixel != that_pixel:
                        n += 1
            if n < best_n:
                best = ascii
                best_n = n
        return best

    def solve_captcha(self, image):
        from collections import defaultdict
        import Image
        N = _captcha_letter_size
        result = {}
        image = image.copy()
        image.convert('L')
        w, h = image.size
        values = defaultdict(int)
        for y in xrange(h):
            for x in xrange(w):
                value = image.getpixel((x, y))
                if value > 0:
                    values[value] += 1
        values = values.items()
        values.sort(key = lambda x: -x[1])
        del values[3:]
        for value, count in sorted(values):
            bi_image = Image.new('1', image.size)
            w, h = image.size
            min_x = w
            min_y = h
            max_x = max_y =  0
            for y in xrange(h):
                for x in xrange(w):
                    if image.getpixel((x, y)) == value:
                        bi_image.putpixel((x, y), 1)
                        if x < min_x:
                            min_x = x
                        elif x > max_x:
                            max_x = x
                        if y < min_y:
                            min_y = y
                        elif y > max_y:
                            max_y = y
            bi_image = bi_image.crop((min_x, min_y, max_x, max_y))
            w, h = bi_image.size
            dx = (N - w) // 2
            dy = (N - h) // 2
            letter = [' ' * N] * dy
            for y in xrange(h):
                line = [' ' * dx]
                for x in xrange(w):
                    line += ('#' if bi_image.getpixel((x, y)) else ' '),
                line += (' ' * (N - w - dx))
                letter += ''.join(line),
            letter += [' ' * N] * (N - h - dy)
            result[min_x] = self._find_letter(letter)
        return ''.join(ascii for x, ascii in sorted(result.iteritems()))

    def download(self):
        import os
        import urllib
        response = self.open(self.start_uri)
        content = response.read()
        captcha_match = _captcha_search(content)
        if captcha_match is None:
            self.api_error(code='c')
        while captcha_match is not None:
            captcha_uri = captcha_match.group(1)
            captcha_uri = urllib.basejoin(self.start_uri, captcha_uri)
            captcha = self.open_novisit(captcha_uri)
            token = self.read_captcha(captcha)
            self.select_form(nr=0)
            self['imagestring'] = token
            response = self.submit()
            content = response.read()
            captcha_match = _captcha_search(content)
        vars = {}
        v1 = _code_v1_search(content)
        if v1 is None:
            self.api_error(code='v1')
        v2 = _code_v2_search(content)
        if v2 is None:
            self.api_error(code='v2')
        vars[v1.group(1)] = chr(int(v1.group(2)))
        vars[v2.group(1)] = v2.group(2) + chr(int(int(v2.group(3)) ** 0.5))
        m = _uri_search(content)
        if m is None:
            self.api_error(code='uri')
        target = m.group(5)
        uri = m.group(1) + vars[m.group(2)] + vars[m.group(3)] + m.group(4) + target
        if os.path.exists(target):
            self.log_info('Nothing to do.')
            return
        m = _wait_search(content)
        if m is None:
            self.api_error(code='wait')
        seconds = int(m.group(1))
        self.sleep(seconds)
        self.wget(uri, target)

# vim:ts=4 sw=4 et
