"""
simple, ugly and really really STUPID web interface for browsing docker-registry
"""

from flask import Flask
from flask import render_template
from flask import redirect
from libs.registry import Registry
from os import environ
from urlparse import urlparse
import re

app = Flask(__name__)
app.config.from_pyfile('web.cfg')

# set REGISTRY_URL from env if key exist
if environ.get("REGISTRY_URL"):
    app.config["REGISTRY_URL"] = environ.get("REGISTRY_URL")

# address for use in docker pull command
app.config["REGISTRY_PULL"] =  urlparse(app.config["REGISTRY_URL"]).netloc

registry = Registry(app.config["REGISTRY_URL"])



@app.route('/')
def index():
    """
    homepage
    """
    return redirect('/repositories')


@app.route('/repositories')
def repositories():
    """
    list all repositories
    """
    res = registry.search()
    results = res['results']

    def sort_key(x):
        library_ns = re.match('library\/(.*)', x['name'])
        if library_ns:
            # so library repositories will be first
            return "-1/{}".format(library_ns.groups(1))
        return x['name']
            
    results_sorted = sorted(results, key=sort_key) 

    for r in results_sorted:
        r['tags'] = registry.get_tags(r['name'])
    
    return render_template('index.html', results=results_sorted)



@app.route('/repository/<path:repo>')
def repository(repo):
    """
    get all tags and images for repository
    """
    tags = registry.get_tags(repo)
    images = registry.get_images(repo)

    # swap key and value
    inv_tag = {v:k for k, v in tags.iteritems()}

    # create ancestry as dict {node,parent} for easy duplicate detection,
    # then make list in format for view (d3)
    ancestry_map = {}
    ancestry_list = []

    for img in images:
        a = registry.get_image_ancestry(img['id'])
        for i in range(len(a)-1,-1,-1):
            if i == len(a)-1:
                ancestry_map[a[i]] = None
            else:
                ancestry_map[a[i]] = a[i+1]

    for k,v in ancestry_map.iteritems():
        name = k
        # if image has tag, show tag instead of hash
        if name in inv_tag:
            name = inv_tag[name]
        else:
            # show only first 12 characters from hash
            name = name[0:12]
        ancestry_list.append({'name': name, 'parent': v if not v else v[0:12]})

    return render_template('repository.html',
                           tags=tags,
                           images=images,
                           repo_name=repo,
                           ancestry_list=ancestry_list)

@app.route('/image/<img>')
def image(img):
    """
    get info about image
    """
    img_info = registry.get_image_info(img)
    a = registry.get_image_ancestry(img)

    ancestry_list = []

    for i in range(len(a)-1,-1,-1):
        if i == len(a)-1:
            ancestry_list.append({'name': a[i][0:12], 'parent': None})
        else:
            ancestry_list.append({'name': a[i][0:12], 'parent': a[i+1][0:12]})

    return render_template('image.html', img_info=img_info, ancestry_list=ancestry_list)


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=4000, debug=True)

