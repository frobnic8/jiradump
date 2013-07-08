"""Parsers for various raw JIRA fields."""

from logging import debug, warning
from collections import Iterable
from datetime import datetime, timedelta


class BasicFieldParser(object):
    """Encodes all values as unicode strings and combines mutliple results into
    a delimited string.
    """

    def __init__(self, field_name, issues, jira, delimiter):
        """Handle any initial setup for the given issue set."""
        self.field_name = unicode(field_name)
        self.delimiter = unicode(delimiter)

    def headers(self):
        """Return an ordered list of headers for the given field as unicode.

        This will be just the field name for fields which don't split into
        multiple columns of output.
        """
        return [unicode(self.field_name)]

    def _parse_one_value(self, raw_value):
        """Parse a single value.

        Overwrite just this method if you want multiple values to be combined
        in one delimited string.

        Fields which split into multiple columns should overwrite this method
        to raise a NotImplemented exception.
        """
        if raw_value:
            return unicode(raw_value)
        else:
            return u''

    def parse_values(self, raw_values):
        """Return an ordered list of the parsed values as unicode.

        This will be a list with a single unicode string for fields which
        do not split into multiple columns. Multiple values will be joined into
        a single delimited string.

        For subclasses which return multiple columns, this and headers must be
        overwritten to provide the same number of items in the returned list.
        """
        if (isinstance(raw_values, basestring) or
                not isinstance(raw_values, Iterable)):
            raw_values = [raw_values]

        return [self.delimiter.join([self._parse_one_value(value)
                                     for value in raw_values])]


class DateTimeFieldParser(BasicFieldParser):
    def _parse_one_value(self, raw_value):
        """Parse the ISO style datetime values into a spreadsheet friendly
        format.

        e.g. 2013-06-04T15:15:36.000-0400 to 2013-06-04 15:15:36
        """
        debug('Parsing raw datetime value: ' + repr(raw_value))
        if raw_value:
            try:
                return unicode(datetime.strptime(raw_value[:19],
                                                 '%Y-%m-%dT%H:%M:%S'))
            except (TypeError, ValueError):
                warning('Could not parse datetime: ' + raw_value)
                return BasicFieldParser._parse_one_value(self, raw_value)
        else:
            return u''


class TimeInStatusFieldParser(BasicFieldParser):

    # These are the crazy Time in Status delimiters we need to parse with.
    PARSING_DELIMITER = '_*|*_'
    PARSING_SUBDELIMITER = '_*:*_'

    def __init__(self, field_name, issues, jira, delimiter):
        """Scan the issues to see which status codes exist in these issues.

        We also use the jira connection to look up the pretty names for the
        status codes.
        """
        # Create a mapping of status IDs to names (including custom statuses).
        # TODO: Add error handling
        self.status_names = dict([(status.id, status.name)
                                  for status in jira.statuses()])

        # scan the issues for the know statuses
        return BasicFieldParser.setup(self, issues, jira, delimiter)

    def headers(self):
        return []

    def _parse_one_value(self, raw_value):
        """This should never be called on parsers that split values into
        multiple columns.
        """
        raise NotImplemented

    # TODO: Support that crazy ass 'Time in Status'
    # TODO: Replace this with a proper, multi-column parsing object.
    def parse_time_in_status(raw_values):
        """Split the time in status raw into a readable string.

        Example data:
        u'1_*:*_1_*:*_584742000_*|*_6_*:*_1_*:*_0_*|*_' + \
        u'10111_*:*_1_*:*_170163000_*|*_10112_*:*_1_*:*_352367000'

        How to split:
          [eggs.split('_*:*_') for eggs in spam.split('_*|*_')]

        The first part is the status code, the second is the number of times in
        that status, the third is the time in milliseconds.

        Ideal output would have multiple columns (two for each status that
        occurs, but only the ones that do occur in the output). One would be
        times in status and the other time in the same status.

        Time is probably best in decimal days.

        Probably want to filter out time in resolved and closed statuses.

        """

        """
        if not raw_value:
            return [u'']

        # TODO: This nastiness is to support a temporary Time in Status parsing
        # until we get a real parser setup.
        global status_names

        # These are the crazy Time in Status delimiters we need to parse with.
        PARSING_DELIMITER = '_*|*_'
        PARSING_SUBDELIMITER = '_*:*_'

        # TODO: This is bad because we IGNORE the user set subdelimiter.
        SUBDELIMITER = ', '
        # TODO: This is also bad and could conflict with user set delimiters.
        SUBSUBDELIMITER = ':'

        parsed = []
        debug('Splitting Raw Time in Status: ' + repr(raw_value))
        for item in raw_value.split(PARSING_DELIMITER):
            debug('Splitting Time in Status item: ' + repr(item))
            split = item.split(PARSING_SUBDELIMITER)
            debug('Split Time in Status item: ' + repr(split))
            split[0] = status_names.get(split[0], 'Unknown ' + split[0])
            # TODO: Add error handling here.
            split[2] = timedelta(milliseconds=int(split[2])).total_seconds()
            split[2] = '%0.2f days' % (split[2] / (60 * 60 * 24))
            debug('Parsed Time in Status item: ' + repr(split))
            parsed.append(SUBSUBDELIMITER.join(split))
        return SUBDELIMITER.join(parsed)
        """
