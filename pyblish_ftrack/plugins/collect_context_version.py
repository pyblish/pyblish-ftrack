import os
import sys
import re

# sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
# import pyblish_ftrack_utils

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
                prefix, version = self.version_get(filename, 'v')
                context.set_data('version', value=int(version))
            except ValueError:
                self.log.warning('Cannot find version string in filename.')
                return None
        else:
            context.set_data('version', value=int(context.data('version')))

        self.log.info('Publish Version: {}'.format(context.data('version')))

    def version_get(self, string, prefix):
        """Extract version information from filenames.  Code from Foundry's
        nukescripts.version_get()"""

        if string is None:
            raise ValueError("Empty version string - no match")

        regex = "[/_.]"+prefix+"\d+"
        matches = re.findall(regex, string, re.IGNORECASE)
        if not len(matches):
            msg = "No \"_"+prefix+"#\" found in \""+string+"\""
            raise ValueError(msg)
        return matches[-1:][0][1], re.search("\d+", matches[-1:][0]).group()
