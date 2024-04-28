'''

    A routers used by databases.
    
    
    I want to make every model use default database and models from devices and references migrate to default and trashbin.

'''

class DeviceRouter:
    
    def allow_migrate(db, app_label, model_name=None, **hints):
        if app_label == "devices":
            return db == "trashbin" or db == "default"
        else:
            return db == "default"

