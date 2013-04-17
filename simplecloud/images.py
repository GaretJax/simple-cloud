from simplecloud import resources


class Image(resources.FilesystemResource):
    pass


class Manager(resources.FilesystemResourceManager):
    resource_class = Image
    resource_name = 'image'
    extension = 'ova'
