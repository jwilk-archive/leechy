# encoding=UTF-8

# Copyright © 2009 Jakub Wilk <jwilk@jwilk.net>
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; version 2 dated June, 1991.
#
# This program is distributed in the hope that it will be useful, but
# WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
# General Public License for more details.

from leechy import Browser

class Browser(Browser):

    pattern = r'^http://[\w-]+[.]wrzuta[.]pl/(film|audio)/\w+/[^/]+$'

    def download(self):

        import urlparse
        protocol, host, target, _, _, _ = urlparse.urlparse(self.start_uri)
        _, type, id, target = target.split('/')
        if type == 'film':
            target += '.flv'
            uri = '/sr/f/%(id)s/0/' % locals()
        elif type == 'audio':
            target += '.mp3'
            uri = '/sr/f/%(id)s' % locals()
        else:
            self.report_api_error('filetype')
        uri = urlparse.urlunparse((protocol, host, uri, None, None, None))
        self.wget(uri, target)

