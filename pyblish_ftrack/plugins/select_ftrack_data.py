import os
import json
import base64
import sys
import ftrack

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
import pyblish_ftrack_utils

import pyblish.api


@pyblish.api.log
class CollectFtrackData(pyblish.api.Selector):
    """Collects ftrack data from FTRACK_CONNECT_EVENT
        Arguments:
            version (int): version number of the publish
    """

    order = pyblish.api.Selector.order + 0.11
    hosts = ['*']
    version = (0, 1, 0)

    def process(self, context):

        decodedEventData = json.loads(
            base64.b64decode(
                os.environ.get('FTRACK_CONNECT_EVENT')
            )
        )

        taskid = decodedEventData.get('selection')[0]['entityId']
        ftrack_data = pyblish_ftrack_utils.get_data(taskid)

        # set ftrack data
        context.set_data('ftrackData', value=ftrack_data)

        self.log.info('Found ftrack data: \n\n%s' % ftrack_data)
