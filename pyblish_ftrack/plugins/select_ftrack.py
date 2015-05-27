import os
import json
import base64
import sys

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
import pyblish_ftrack_utils

import pyblish.api


@pyblish.api.log
class SelectFtrack(pyblish.api.Selector):
    """Collects ftrack data from FTRACK_CONNECT_EVENT"""

    hosts = ['*']
    version = (0, 1, 0)


    def process_context(self, context):

        decodedEventData = json.loads(
            base64.b64decode(
                os.environ.get('FTRACK_CONNECT_EVENT')
            )
        )

        taskid = decodedEventData.get('selection')[0]['entityId']

        ftrackData = pyblish_ftrack_utils.getData(taskid)

        context.set_data('ftrackData', value=ftrackData)

        try:
            (prefix, version) = pyblish_utils.version_get(filename, 'v')
        except:
            self.log.warning('Cannot publish workfile which is not versioned.')
            return

        context.set_data('version', value=version)
        context.set_data('vprefix', value=prefix)

        self.log.info('Found ftrack data')