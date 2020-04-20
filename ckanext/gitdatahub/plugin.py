import logging
import ckan.plugins as plugins
import ckan.plugins.toolkit as toolkit
from ckanext.gitdatahub.src.ckan_to_git import CKANGitClient

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
        token = toolkit.config.get('ckanext.gitdatahub.access_token')
        try:
            client = CKANGitClient(token, pkg_dict)
            
            # Create the datapackage
            client.create_datapackage()
            
            # Create the gitattributes            
            client.create_gitattributes()
            
            # Create the lfscomfig
            git_lfs_server_url = toolkit.config.get('ckanext.gitdatahub.git_lfs_server_url')
            client.create_lfsconfig(git_lfs_server_url)
        
        except Exception as e:
            log.exception('Cannot create {} repository.'.format(pkg_dict['name']))

    def after_update(self, context, pkg_dict):
        # Get a complete dict to also save resources data.
        pkg_dict = toolkit.get_action('package_show')(
            {},
            {'id': pkg_dict['id']}
        )
        token = toolkit.config.get('ckanext.gitdatahub.access_token')
        try:
            client = CKANGitClient(token, pkg_dict)
        
            # Update the datapackage
            client.update_datapackage()
        
        except Exception as e:
            log.exception('Cannot update {} repository.'.format(pkg_dict['name']))

        # Create/Update the lfs pointers
        client.create_or_update_lfspointerfile()

    def delete(self, entity):
        token = toolkit.config.get('ckanext.gitdatahub.access_token')
        try:
            client = CKANGitClient(token, entity=entity.name)
            # Commented because dangerous to use with personal token
            client.delete_repo()
        
        except Exception as e:
            log.exception('Cannot delete {} repository.'.format(entity.name))

