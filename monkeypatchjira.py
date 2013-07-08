"""Monkeypatch jira to have basic __str__ and __repr__ methods for Resource."""
# This import can be removed if/when the following pull request for jira-python
# is approved and merged:
# https://bitbucket.org/bspeakmon/jira-python/pull-request/25/added-__str__-and-__repr__-support-to-the/diff
import jira.resources

if jira.resources.Resource.__str__ == object.__str__:
    # A prioritized list of the keys in self.raw most likely to contain a human
    # readable name or identifier, or that offer other key information.
    jira.resources.Resource._READABLE_IDS = ('displayName', 'key', 'name',
                                             'filename', 'value', 'scope',
                                             'votes', 'id', 'mimeType',
                                             'closed')

    def __resource_str(self):
        """Provide a short, pretty name for this jira resource."""
        # Return the first value we find that is likely to be human readable.
        for name in self._READABLE_IDS:
            if name in self.raw:
                pretty_name = unicode(self.raw[name])
                # Include any child to support nested select fields.
                if hasattr(self, 'child'):
                    pretty_name += ' - ' + unicode(self.child)
                return pretty_name

        # If all else fails, use repr to make sure we get something.
        return repr(self)

    jira.resources.Resource.__str__ = __resource_str

    def __resource_repr(self):
        """Provide a more detailed name for this jira resource."""
        # Identify the class and include any and all relevant values.
        names = []
        for name in self._READABLE_IDS:
            if name in self.raw:
                names.append(name + '=' + repr(self.raw[name]))
        return '<JIRA %s: %s>' % (self.__class__.__name__, ', '.join(names))

    jira.resources.Resource.__repr__ = __resource_repr
