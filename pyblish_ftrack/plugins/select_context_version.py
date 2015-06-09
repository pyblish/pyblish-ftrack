import os
import sys

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
import pyblish_ftrack_utils

import pyblish.api


@pyblish.api.log
class SelectContextVersion(pyblish.api.Selector):
    """Finds version in the filename or passes the one found in the context
        Arguments:
        version (int, optional): version number of the publish
    """

    order = pyblish.api.Selector.order + 0.1
    hosts = ['*']
    version = (0, 1, 0)

    def process(self, context):

        # Get version number
        if not context.has_data('version'):
            directory, filename = os.path.split(context.data('currentFile'))
            try:
                prefix, version = pyblish_ftrack_utils.version_get(filename, 'v')
                context.set_data('version', value=int(version))
            except ValueError:
                self.log.warning('Cannot find version string in filename.')
                return None
        else:
            context.set_data('version', value=int(context.data('version')))

        self.log.info('Publish Version: {}'.format(context.data('version')))
