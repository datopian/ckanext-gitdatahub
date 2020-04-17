import json
from ckanapi.datapackage import dataset_to_datapackage

def create_datapackage(pkg_dict, repo):
    body = dataset_to_datapackage(pkg_dict)
    repo.create_file(
        'datapackage.json',
        'Create datapackage.json',
        json.dumps(body, indent=2)
        )

def create_gitattributes(repo):
    repo.create_file(
    '.gitattributes',
    'Create .gitattributes',
    'data/* filter=lfs diff=lfs merge=lfs -text\n'
    )

def create_lfsconfig(pkg_dict, repo, auth_user, git_lfs_server_url):
    repoUrl = '{}/{}/{}'.format(git_lfs_server_url,auth_user.html_url.split('/')[-1],pkg_dict['name'])
    repo.create_file(
        '.lfsconfig',
        'Create .lfsconfig',
        '[remote "origin"]\n\tlfsurl = ' + repoUrl
        )    

def update_datapackage(pkg_dict, repo):
    contents = repo.get_contents("datapackage.json")
    body = dataset_to_datapackage(pkg_dict)
    repo.update_file(
        contents.path,
        "Update datapackage.json",
        json.dumps(body, indent=2),
        contents.sha
        )

def create_lfspointerfile(repo, obj):
    sha256 = obj['sha256']
    size = obj['size']
    lfs_pointer_body ='version https://git-lfs.github.com/spec/v1\noid sha256:{}\nsize {}\n'.format(sha256, size)
    repo.create_file(
    "data/{}".format(obj['name']),
    "Create LfsPointerFile",
    lfs_pointer_body,
    )

def update_lfspointerfile(repo, obj):
    contents = repo.get_contents("data/{}".format(obj['name']))
    sha256 = obj['sha256']
    size = obj['size']
    lfs_pointer_body ='version https://git-lfs.github.com/spec/v1\noid sha256:{}\nsize {}\n'.format(sha256, size)
    repo.update_file(
        contents.path,
        "Update LfsPointerFile",
        lfs_pointer_body,
        contents.sha
        )
