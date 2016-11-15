# pyblish-ftrack

[![Code Health](https://landscape.io/github/pyblish/pyblish-ftrack/master/landscape.svg?style=flat)](https://landscape.io/github/pyblish/pyblish-ftrack/master)

Pyblish for FTrack

## Usage

To succesfully publish an instance to ftrack using this extension you need to append a few data members to the instance you want to publish.

**Required data**

- ftrackComponents (dict) - Dictionary of dictionaries where each key is a component name. There are required and optional keys:
  - **Required keys**
    - *path* (str): Holds the path to the file being published.
  - **Optional keys**
    - *reviewable* (bool): Tells extension whether you want the component to be uploaded to ftrack servers and made available for web-review.
    - *location* (ftrack.Location): If you set this data member on a component, the component will be added to that location when creating the component. By default all components will be added to "ftrack.unmanaged" location.

```python
location = ftrack.Location("custom_location")
ftrackComponents = {
    "sequence": {"path": "path/to/file.%04d.exr", "location"=location},
    "movie":    {"path": "path/to/file.mp4", "reviewable"=True},
}

instance.data['ftrackComponents'] = ftrackComponents
```

**Optional data:**

- ftrackAssetName - Name of ftrack asset where you want your AssetVersion to be created. (Context data)
 - If you set this data, extensionwill try to find an existing ftrack asset with given name and attach the version to it. If such asset is not found, a new one will be created.

```python
# Example code to set ftrackAssetName data
context.data["ftrackAssetName"] = "myAsset"
```

- version - Version number of the publish (Context data)
 - ftrack extension needs to know a version number the publish taking place so it can set ftrack version to the same number. If you set version yourself, it will be pick up by plugins and used. If not, extension will try to get the version number from currentFile context.

```python
# Example code to set ftrackAssetName data
context.data["version"] = 2
```

**Publish from Ftrack**

Environment variables to set before launching ftrack-connect.

- Add ```pyblish-ftrack/ftrack_event_plugin_path``` to ```FTRACK_EVENT_PLUGIN_PATH```
- Add ```pyblish-win/pythonpath``` to ```PYTHONPATH```

Publish action will appear in the available actions. When launched it will ask for a folder. This will be the current working directory (cwd), for the session, which can be access in plugins through ```os.getcwd()```

Currently only tasks have the Publish action.

**Debug Messages**

By default Ftrack outputs a lot of debug messages. Still can be disabled with:

```python
import logging
logging.getLogger("ftrack_api").setLevel(logging.INFO)
```
