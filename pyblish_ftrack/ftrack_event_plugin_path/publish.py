import sys
import argparse
import logging
import os
import getpass
import pprint
import subprocess

import ftrack
import ftrack_connect.application

class Publish(ftrack.Action):
    '''Custom action.'''

    #: Action identifier.
    identifier = 'publish'

    #: Action label.
    label = 'Publish'


    def __init__(self):
        '''Initialise action handler.'''
        self.log = logging.getLogger(
            __name__ + '.' + self.__class__.__name__
        )

        self.applicationStore = ApplicationStore()

    def register(self):
        '''Register action.'''
        ftrack.EVENT_HUB.subscribe(
            'topic=ftrack.action.discover and source.user.username={0}'.format(
                getpass.getuser()
            ),
            self.discover
        )

        ftrack.EVENT_HUB.subscribe(
            'topic=ftrack.action.launch and source.user.username={0} '
            'and data.actionIdentifier={1}'.format(
                getpass.getuser(), self.identifier
            ),
            self.launch
        )

    def isValidSelection(self, selection):
        '''Return true if the selection is valid.

        Legacy plugins can only be started from a single Task.

        '''
        if (
            len(selection) != 1 or
            selection[0]['entityType'] != 'task'
        ):
            return False

        entity = selection[0]
        task = ftrack.Task(entity['entityId'])

        if task.getObjectType() != 'Task':
            return False

        return True

    def discover(self, event):
        '''Return discovered applications.'''
        if not self.isValidSelection(
            event['data'].get('selection', [])
        ):
            return

        items = []
        applications = self.applicationStore.applications
        applications = sorted(
            applications, key=lambda application: application['label']
        )

        for application in applications:
            applicationIdentifier = application['identifier']
            label = application['label']
            items.append({
                'actionIdentifier': self.identifier,
                'label': label,
                'icon': application.get('icon', 'default'),
                'applicationIdentifier': applicationIdentifier
            })

        return {
            'items': items
        }

    def launch(self, event):
        data = event['data']
        selection = data.get('selection', [])

        ftrack.EVENT_HUB.publishReply(event,
            data={
                'success': True,
                'message': 'Pyblish Launched!'
            }
        )

        entity = selection[0]
        task = ftrack.Task(entity['entityId'])
        os.environ['FTRACK_TASKID'] = task.getId()
        applicationIdentifier = event['data']['applicationIdentifier']

        path = os.path.join(os.path.dirname(__file__),
                            'environment_wrapper.py')

        app = ApplicationStore()
        app._modifyApplications(path)
        launcher = ftrack_connect.application.ApplicationLauncher(app)

        launcher.launch(applicationIdentifier)


class ApplicationStore(ftrack_connect.application.ApplicationStore):

    def _modifyApplications(self, path=''):
        self.applications = self._discoverApplications(path=path)

    def _discoverApplications(self, path=''):
        '''Return a list of applications that can be launched from this host.

        An application should be of the form:

            dict(
                'identifier': 'name_version',
                'label': 'Name version',
                'path': 'Absolute path to the file',
                'version': 'Version of the application',
                'icon': 'URL or name of predefined icon'
            )

        '''

        launchArguments = []
        if path:
            launchArguments = [path]

        return self._searchFilesystem(
            expression=['C:\\', 'Python*', 'python.exe'],
            label='Publish',
            applicationIdentifier='publish',
            icon="https://raw.githubusercontent.com/pyblish/pyblish-ftrack/master/pyblish_ftrack/ftrack_event_plugin_path/icon.png",
            launchArguments=launchArguments
        )


def register(registry, **kw):
    '''Register action. Called when used as an event plugin.'''
    logging.basicConfig(level=logging.INFO)
    action = Publish()
    action.register()


def main(arguments=None):
    '''Set up logging and register action.'''
    if arguments is None:
        arguments = []

    parser = argparse.ArgumentParser()
    # Allow setting of logging level from arguments.
    loggingLevels = {}
    for level in (
        logging.NOTSET, logging.DEBUG, logging.INFO, logging.WARNING,
        logging.ERROR, logging.CRITICAL
    ):
        loggingLevels[logging.getLevelName(level).lower()] = level

    parser.add_argument(
        '-v', '--verbosity',
        help='Set the logging output verbosity.',
        choices=loggingLevels.keys(),
        default='info'
    )
    namespace = parser.parse_args(arguments)

    '''Register action and listen for events.'''
    logging.basicConfig(level=loggingLevels[namespace.verbosity])

    ftrack.setup()
    action = Publish()
    action.register()

    ftrack.EVENT_HUB.wait()


if __name__ == '__main__':
    raise SystemExit(main(sys.argv[1:]))
