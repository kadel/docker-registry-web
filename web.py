"""
simple, ugly and really really STUPID web interface for browsing docker-registry
"""

from flask import Flask
from flask import render_template
from libs.registry import Registry
import treelib

app = Flask(__name__)
app.config.from_pyfile('web.cfg')

registry = Registry(app.config["REGISTRY_URL"])


@app.route('/')
def index():
    """
    list all repositories
    """
    res = registry.search()
    results = res['results']

    for r in results:
        r['tags'] = registry.get_tags(r['name'])
    
    return render_template('index.html', results=results)


@app.route('/repository/<path:repo>')
def repository(repo):
    """
    get all tags and images for repository
    """
    tags = registry.get_tags(repo)
    images = registry.get_images(repo)


    # create ancestry in dict {node,parent} for easy duplicate detection,
    # then make list in as list in format for view (d3)
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
        ancestry_list.append({'name': k[0:12], 'parent': v if not v else v[0:12]})

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

