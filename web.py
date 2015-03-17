"""
simple, ugly and really really STUPID web interface for browsing docker-registry
"""

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from libs.model import Base
from libs.model import Tag

from flask import Flask
from flask import render_template
from flask import redirect
from flask import request

from libs.registry import Registry
from os import environ
from urlparse import urlparse
from libs.forms import DescendantsSearchByTagForm
from libs.forms import DescendantsSearchByIdForm
from libs.ImageDescendants import ImageDescendants

import re

app = Flask(__name__)
app.config.from_pyfile('web.cfg')

# set REGISTRY_URL from env if key exist
if environ.get("REGISTRY_URL"):
    app.config["REGISTRY_URL"] = environ.get("REGISTRY_URL")

# address for use in docker pull command
app.config["REGISTRY_PULL"] =  urlparse(app.config["REGISTRY_URL"]).netloc

registry = Registry(app.config["REGISTRY_URL"])


engine = create_engine('sqlite:///sqlalchemy_example.db')
# Bind the engine to the metadata of the Base class so that the
# declaratives can be accessed through a DBSession instance
Base.metadata.bind = engine

DBSession = sessionmaker(bind=engine)

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

    DBSession = sessionmaker(bind=engine)
    session = DBSession()

    for k,v in ancestry_map.iteritems():
        name = k
        fullname=k
        # if image has tag, show tag instead of hash
        if name in inv_tag:
            name = inv_tag[name]
        else:
            tagFromDb = session.query(Tag).filter(Tag.id == fullname).first()
            if not tagFromDb is None:
              fullname = tagFromDb.layer + ":" + tagFromDb.tag

            # show only first 12 characters from hash
            name = name[0:12]

        ancestry_list.append({'imageid': fullname, 'name': name, 'parent': v if not v else v[0:12]})

    session.close();

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

    #find all tags for given image
    DBSession = sessionmaker(bind=engine)
    session = DBSession()
    print "Debug: finding tags for \"" + str(img) + "\""
    allImageTags = [(taginfo.layer, taginfo.tag) for taginfo in session.query(Tag).filter(Tag.id == img).all()]
    session.close();

    ancestry_list = []

    DBSession = sessionmaker(bind=engine)
    session = DBSession()

    for i in range(len(a)-1,-1,-1):
        fullIndexId = a[i]
        nodeInfo=registry.get_image_info(fullIndexId)

        if 'author' in nodeInfo:
            author=nodeInfo['author']
            gtposition=author.find("<");
            if gtposition>0:
                author=author[:gtposition - 1];
        else:
            author=None

        if 'created' in nodeInfo:
            created=nodeInfo['created']
        else:
            created=0

        #this is slow
        allImageTags = [(taginfo.layer, taginfo.tag) for taginfo in session.query(Tag).filter(Tag.id == fullIndexId).all()]

        if not len(allImageTags) == 0:
            pair = allImageTags[0] #TODO choose the best tag.
            tagName = pair[0] + ":" + pair[1]
        else:
            tagName = None

        if i == len(a)-1:
            ancestry_list.append({'maintagname': tagName, 'imageid': fullIndexId, 'name': fullIndexId[0:12], 'author':  author, 'created':  created, 'parent': None})
        else:
            ancestry_list.append({'maintagname': tagName, 'imageid': fullIndexId, 'name': fullIndexId[0:12], 'author':  author, 'created':  created, 'parent': a[i+1][0:12]})

    session.close();
    return render_template('image.html', img_info=img_info, ancestry_list=ancestry_list, allImageTags=allImageTags)

@app.route('/indexdrop/')
def indexdrop():
    image_descendants = ImageDescendants(registry)
    image_descendants.deleteAll()
    return None

@app.route('/indexupdate/', methods=['GET', 'POST'])
def imageindexupdate():
  """
  Finds new images in all repositories and saves them to DB.
  :return:
  """
  if 'doimageupdate' in request.args:
    image_descendants = ImageDescendants(registry)
    indexupdateresult = image_descendants.updateDescendantIndex()
  elif 'dotagupdate' in request.args:
    image_descendants = ImageDescendants(registry)
    indexupdateresult = image_descendants.updateTagIndex()
  else:
    indexupdateresult = None

  return render_template('indexupdate.html', indexupdateresult=indexupdateresult)


@app.route('/descendants/byid/<id>/', methods=('GET', 'POST'))
def descendantsbyid(id):
    form = DescendantsSearchByIdForm(csrf_enabled=False)

    if form.validate_on_submit():
        return redirect('/descendants/byid/' + str(form.rawid.data))

    form.rawid.data=id

    image_descendants = ImageDescendants(registry)
    result = image_descendants.listDescendants(id.strip())

    imageIndexed=True;
    if len(result) == 0:
        imageIndexed=image_descendants.imageIsIndexed(id.strip())

    return render_template('descendants.html', result=result, form=form, imageIndexed=imageIndexed)

@app.route('/descendants/bylayer/<path:layername>', methods=('GET', 'POST'))
def descendantsbylayer(layername):
    form = DescendantsSearchByTagForm(csrf_enabled=False)

    layername = layername.strip()
    tags = registry.get_tags(layername)
    tagvalue=form.tag.data

    form.tag.choices = [(value, key) for key, value in tags.iteritems()]
    form.layer = layername

    submited = form.validate_on_submit()
    result = None

    if submited:
        image_descendants = ImageDescendants(registry)
        result = image_descendants.listDescendants(tagvalue)


    return render_template('descendants.html', result=result, form=form, layername=layername, submited=submited)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=4000, debug=True)

