import pkg_resources

# Note: we can remove this and replace it with a better package name
# when doing https://github.com/mozilla-services/kinto-dist/issues/1928
__version__ = pkg_resources.get_distribution("kinto-dist").version


def includeme(config):
    config.include("kinto_remote_settings.changes")
    config.include("kinto_remote_settings.signer")
