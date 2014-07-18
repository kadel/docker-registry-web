"""
guick, simple and STUPID wrapper around docker-registry api
"""

import requests
import simplejson as json

class Registry(object):

    def __init__(self, url):
        self.url = url    

    def search(self, query=''):
        res = self._do_get('search?q={0}'.format(query))
        return res

    def get_tags(self, repo):
        """
        list all tags for repository
        """
        res = self._do_get('repositories/{0}/tags'.format(repo))
        return res

    def get_images(self, repo):
        """
        list all images for repository
        """
        res = self._do_get('repositories/{0}/images'.format(repo))
        return res

    def get_image_info(self, img):
        """
        get json info about image
        """
        res = self._do_get('images/{0}/json'.format(img))
        return res

    def get_image_ancestry(self, img):
        '''
        get ancestors for image
        '''
        res = self._do_get('images/{0}/ancestry'.format(img))
        return res


    def _do_get(self, path):
        req = requests.get('{0}/{1}'.format(self.url, path))
        if req.status_code == 200:
            if req.headers['content-type'] == 'application/json':
                return json.loads(req.text)
            else:
                raise Exception('Unknown content-type: {0}'.format(req.headers['content-type']))
        else:
            raise Exception('Unknown status code: {0}, url:{1}'.format(req.status_code, req.url))    

