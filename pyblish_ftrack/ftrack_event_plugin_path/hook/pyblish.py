import logging
import os
import getpass
import pprint

import ftrack
import ftrack_connect.application


class PyblishAction(object):
    """Launch Pyblish action."""

    # Unique action identifier.
    identifier = "pyblish-launch-action"

    def __init__(self, applicationStore, launcher):
        """Initialise action with *applicationStore* and *launcher*.

        *applicationStore* should be an instance of
        :class:`ftrack_connect.application.ApplicationStore`.

        *launcher* should be an instance of
        :class:`ftrack_connect.application.ApplicationLauncher`.

        """
        super(PyblishAction, self).__init__()

        self.logger = logging.getLogger(
            __name__ + "." + self.__class__.__name__
        )

        self.applicationStore = applicationStore
        self.launcher = launcher

        if self.identifier is None:
            raise ValueError("The action must be given an identifier.")

    def register(self):
        """Register discover actions on logged in user."""
        ftrack.EVENT_HUB.subscribe(
            "topic=ftrack.action.discover and source.user.username={0}".format(
                getpass.getuser()
            ),
            self.discover
        )

        ftrack.EVENT_HUB.subscribe(
            "topic=ftrack.action.launch and source.user.username={0} "
            "and data.actionIdentifier={1}".format(
                getpass.getuser(), self.identifier
            ),
            self.launch
        )

    def is_valid_selection(self, selection):
        """Return true if the selection is valid."""
        if (
            len(selection) != 1 or
            selection[0]["entityType"] != "task"
        ):
            return False

        entity = selection[0]
        task = ftrack.Task(entity["entityId"])

        if task.getObjectType() != "Task":
            return False

        return True

    def discover(self, event):
        """Return available actions based on *event*.

        Each action should contain

            actionIdentifier - Unique identifier for the action
            label - Nice name to display in ftrack
            variant - Variant or version of the application.
            icon(optional) - predefined icon or URL to an image
            applicationIdentifier - Unique identifier to identify application
                                    in store.

        """
        if not self.is_valid_selection(
            event["data"].get("selection", [])
        ):
            return

        items = []
        applications = self.applicationStore.applications
        applications = sorted(
            applications, key=lambda application: application["label"]
        )

        for application in applications:
            applicationIdentifier = application["identifier"]
            label = application["label"]
            items.append({
                "actionIdentifier": self.identifier,
                "label": label,
                "variant": application.get("variant", None),
                "description": application.get("description", None),
                "icon": application.get("icon", "default"),
                "applicationIdentifier": applicationIdentifier
            })

        return {
            "items": items
        }

    def launch(self, event):
        """Callback method for Pyblish action."""
        applicationIdentifier = (
            event["data"]["applicationIdentifier"]
        )

        context = event["data"].copy()
        context["source"] = event["source"]

        return self.launcher.launch(applicationIdentifier, context)


class ApplicationStore(ftrack_connect.application.ApplicationStore):

    def _discoverApplications(self):
        """Return a list of applications that can be launched from this host.

        An application should be of the form:

            dict(
                "identifier": "name_version",
                "label": "Name version",
                "path": "Absolute path to the file",
                "version": "Version of the application",
                "icon": "URL or name of predefined icon"
            )

        """

        applications = []
        icon = "https://raw.githubusercontent.com/pyblish/pyblish-ftrack/"
        icon += "master/pyblish_ftrack/ftrack_event_plugin_path/icon.png"

        python_path = self.check_executable("python")
        if python_path:
            applications.append(
                {
                    "description": None,
                    "icon": icon,
                    "identifier": "pyblish",
                    "label": "Pyblish",
                    "launchArguments": [
                        os.path.abspath(
                            os.path.join(
                                os.path.dirname(__file__), "..", "main.py"
                            )
                        )
                    ],
                    "path": python_path,
                    "varient": "",
                    "version": ""
                }
            )

        self.logger.debug(
            "Discovered applications:\n{0}".format(
                pprint.pformat(applications)
            )
        )

        return applications

    def check_executable(self, executable):
        """ Checks to see if an executable is available.

        Args:
            executable (str): The name of executable without extension.

        Returns:
            bool: True for executable existance, False for non-existance.
        """

        def is_exe(fpath):
            return os.path.isfile(fpath) and os.access(fpath, os.X_OK)

        fpath, fname = os.path.split(executable)
        if fpath:
            if is_exe(executable):
                return executable
        else:
            for path in os.environ["PATH"].split(os.pathsep):
                path = path.strip('"')
                exe_file = os.path.join(path, executable)
                if is_exe(exe_file):
                    return exe_file
                if is_exe(exe_file + ".exe"):
                    return exe_file + ".exe"

        return None


class ApplicationLauncher(ftrack_connect.application.ApplicationLauncher):
    """Custom launcher to modify environment before launch."""

    def __init__(self, application_store):
        super(ApplicationLauncher, self).__init__(application_store)

    def _getApplicationEnvironment(self, application, context=None):
        """Override to modify environment before launch."""

        # Make sure to call super to retrieve original environment
        # which contains the selection and ftrack API.
        environment = super(
            ApplicationLauncher, self
        )._getApplicationEnvironment(application, context)

        entity = context["selection"][0]
        task = ftrack.Task(entity["entityId"])

        environment["FTRACK_TASKID"] = task.getId()

        return environment


def register(registry, **kw):
    """Register hooks."""

    # Validate that registry is the correct ftrack.Registry. If not,
    # assume that register is being called with another purpose or from a
    # new or incompatible API and return without doing anything.
    if registry is not ftrack.EVENT_HANDLERS:
        # Exit to avoid registering this plugin again.
        return

    # Create store containing applications.
    applicationStore = ApplicationStore()

    # Create a launcher with the store containing applications.
    launcher = ApplicationLauncher(applicationStore)

    # Create action and register to respond to discover and launch actions.
    action = PyblishAction(applicationStore, launcher)
    action.register()
