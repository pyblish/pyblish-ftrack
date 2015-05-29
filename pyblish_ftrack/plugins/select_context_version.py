import os
import json
import base64
import sys
import ftrack

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
import pyblish_ftrack_utils

import pyblish.api


@pyblish.api.log
class SelectContextVersion(pyblish.api.Selector):
    """Collects ftrack data from FTRACK_CONNECT_EVENT"""

    order = pyblish.api.Selector.order + 0.1
    hosts = ['*']
    version = (0, 1, 0)

    def process_context(self, context):

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
