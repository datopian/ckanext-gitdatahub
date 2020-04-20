import logging
import ckan.plugins as plugins
import ckan.plugins.toolkit as toolkit

from github import Github, UnknownObjectException
from ckanext.gitdatahub.src.ckan_to_git import *

log = logging.getLogger(__name__)

class GitDataHubException(Exception):
    pass


class GitdatahubPlugin(plugins.SingletonPlugin):
    plugins.implements(plugins.IConfigurer)
    plugins.implements(plugins.IPackageController, inherit=True)

    # IConfigurer
    def configure(self, config):
        # TODO: This doesn't work
        if not config['ckanext.gitdatahub.access_token']:
            msg = 'ckanext.gitdatahub.access_token is missing from config file'
            raise GitDataHubException(msg)

    def update_config(self, config_):
        toolkit.add_template_directory(config_, 'templates')
        toolkit.add_public_directory(config_, 'public')
        toolkit.add_resource('fanstatic', 'gitdatahub')

    def after_create(self, context, pkg_dict):
        log.info('################### After Create! ###################')
        token = toolkit.config.get('ckanext.gitdatahub.access_token')
        try:
            g = Github(token)
            auth_user = g.get_user()
            repo = auth_user.create_repo(pkg_dict['name'], pkg_dict['notes'])
            
            # Create the datapackage
            create_datapackage(pkg_dict, repo)
            
            # Create the gitattributes            
            create_gitattributes(repo)
            
            # Create the lfscomfig
            git_lfs_server_url = toolkit.config.get('ckanext.gitdatahub.git_lfs_server_url')
            create_lfsconfig(pkg_dict, repo, auth_user, git_lfs_server_url)
        
        except Exception as e:
            log.exception('Cannot create {} repository.'.format(pkg_dict['name']))

    def after_update(self, context, pkg_dict):
        #TODO: What happens if user changes the package name? Should we create a new repo?
        # Get a complete dict to also save resources data.
        log.info('################### After Update! ###################')
        pkg_dict = toolkit.get_action('package_show')(
            {},
            {'id': pkg_dict['id']}
        )
        token = toolkit.config.get('ckanext.gitdatahub.access_token')

        try:
            g = Github(token)
            auth_user = g.get_user()
            repo = auth_user.get_repo(pkg_dict['name'])
        
            # Update the datapackage
            update_datapackage(pkg_dict, repo)
        
        except Exception as e:
            log.exception('Cannot update {} repository.'.format(pkg_dict['name']))
        
        # Create/Update the lfs pointers
        try:
            lfs_pointers = [obj.name for obj in repo.get_contents("data")]
            lfs_pointers = {obj:get_sha256(obj, repo) for obj in lfs_pointers}
        
        except UnknownObjectException as e:
            lfs_pointers = dict()
        
        for obj in pkg_dict['resources']:
            if obj['name'] not in lfs_pointers.keys():
                create_lfspointerfile(repo, obj)
        
            elif obj['sha256'] != lfs_pointers[obj['name']]:
                update_lfspointerfile(repo, obj)

    def delete(self, entity):
        token = toolkit.config.get('ckanext.gitdatahub.access_token')
        try:
            g = Github(token)
            auth_user = g.get_user()
            repo = auth_user.get_repo(entity.name)
        
            # Commented because dangerous to use with personal token
            repo.delete()
            log.info("{} repository deleted.".format(entity.name))
        
        except Exception as e:
            log.exception('Cannot delete {} repository.'.format(entity.name))

def get_sha256(lfspointerfile, repo):
    return str(repo.get_contents("data/{}".format(lfspointerfile)).decoded_content).split('\n')[1].split(':')[-1]
