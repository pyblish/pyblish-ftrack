import os

import pyblish_qml.app
import pyblish_rpc.server
import pyblish_rpc.client
import ftrack


def main(port=9080):
    # setting Pyblish Window title
    task = ftrack.Task(os.environ['FTRACK_TASKID'])
    path = [task.getName()]
    for p in task.getParents():
        path.append(p.getName())

    path = ' / '.join(list(reversed(path)))
    pyblish_qml.settings.WindowTitle = path

    app_path = pyblish_qml.app.APP_PATH
    app = pyblish_qml.app.Application(app_path)
    app.__debugging__ = True
    app.listen()

    proxy = pyblish_rpc.client.Proxy(port)
    if not proxy.ping():
        os.environ["PYBLISH_CLIENT_PORT"] = str(port)
        pyblish_rpc.server.start_async_production_server(port)
        print("Running standalone RPC server @ 127.0.0.1:%s" % port)

    app.show_signal.emit(port, {})

    print("Running Pyblish QML standalone @ 127.0.0.1:9090")
    return app.exec_()


if __name__ == '__main__':
    main()
