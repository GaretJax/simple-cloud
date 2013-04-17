import fablib

fablib.loadpackages(
    # Add here the packages you want to load.
    # We already added a selection of the most used ones.
    'apps', 'project', 'django', 'dev',
)

fablib.environment({
    # Here you can configure your environment.
    # Each key in this dict will be added to the environment
    # in which your tasks will be run.
    'hosts': [
        'example.com',
    ],
    'user': '',
})
