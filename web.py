"""
simple, ugly and really really STUPID web interface for browsing docker-registry
"""

from flask import Flask
from flask import render_template
from libs.registry import Registry

app = Flask(__name__)
app.config.from_pyfile('web.cfg')

registry = Registry(app.config["REGISTRY_URL"])


@app.route('/')
def index():
    """
    list all repositories
    """
    result = registry.search()
    return render_template('index.html', result=result)


@app.route('/repository/<path:repo>')
def repository(repo):
    """
    get all tags and images for repository
    """
    tags = registry.list_tags(repo)
    images = registry.list_images(repo)

    return render_template('repository.html',
            tags=tags,
            images=images,
            repo_name=repo)

@app.route('/image/<img>')
def image(img):
    """
    get info about image
    """
    img = registry.image_info(img)
    return render_template('image.html', img=img)


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=4000, debug=True)

