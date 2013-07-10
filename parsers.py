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
        to raise a NotImplementedError exception and instead do their work by
        overwriting parse_values() and headers().
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
    """Converts JIRA's ISO style date times in more spreadsheet friendly form.

    e.g. 2013-06-04T15:15:36.000-0400 to 2013-06-04 15:15:36
    """

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
    """Parse the crazy custom Time in Status field into multple columns."""

    # These are the crazy Time in Status delimiters we need to parse with.
    PARSING_DELIMITER = '_*|*_'
    PARSING_SUBDELIMITER = '_*:*_'

    FIRST_STATUSES = ['Open']
    LAST_STATUSES = ['Closed']

    def __init__(self, field_name, issues, jira, delimiter):
        """Scan the issues to see which status codes exist in these issues.

        We also use the jira connection to look up the pretty names for the
        status codes.
        """
        # Create a mapping of status IDs to names (including custom statuses).
        debug('Mapping status IDs to names.')
        # TODO: Add error handling
        self.status_names = dict([(status.id, unicode(status.name))
                                  for status in jira.statuses()])

        # Lookup the ID for Time in Status.
        debug("Looking up 'Time in Status' field ID.")
        # TODO: Add error handling
        for field in jira.fields():
            if field['name'] == 'Time in Status':
                time_in_status_id = field['id']
                break

        statuses = set()
        # Scan the issues for the know statuses
        for issue in issues:
            time_in_status = getattr(issue.fields, time_in_status_id, u'')
            statuses.update(self._parse_time_in_status(time_in_status).keys())

        # Assign an order to the statuses found making sure a few certain
        # statuses are in certain positions.
        prefix = []
        postfix = []
        # Pull out any statuses we want to be first in order.
        for status in self.FIRST_STATUSES:
            if status in statuses:
                statuses.remove(status)
                prefix.append(status)
        for status in self.LAST_STATUSES:
            if status in statuses:
                statuses.remove(status)
                postfix.append(status)
        # Build the ordered list of statuses.
        self.statuses = prefix + sorted(list(statuses)) + postfix

        # Call the super init to be safe.
        BasicFieldParser.__init__(self, field_name, issues, jira, delimiter)

    def headers(self):
        headers = []
        for status in self.statuses:
            headers += [status + u' Count', status + u' Days']
        return headers

    def _parse_time_in_status(self, raw_time_in_status):
        """Split the time in status raw into a readable dict.

        Example data:
        u'1_*:*_1_*:*_584742000_*|*_6_*:*_1_*:*_0_*|*_' + \
        u'10111_*:*_1_*:*_170163000_*|*_10112_*:*_1_*:*_352367000'

        How to split:
          [eggs.split('_*:*_') for eggs in spam.split('_*|*_')]

        The first part is the status code, the second is the number of times in
        that status, the third is the time in milliseconds.

        The dict is keyed to the human readable status name, with a value
        for count which is the integer times in that status
        The duration is converted to a timedelta.
        """
        # Split the giant string into invidicual status times and convert the
        # status codes and times into human readable formats.
        if not raw_time_in_status:
            return {}
        debug('Parsing Raw Time in Status: ' + repr(raw_time_in_status))
        status_times = {}
        for status_time in raw_time_in_status.split(self.PARSING_DELIMITER):
            status, count, msecs = status_time.split(self.PARSING_SUBDELIMITER)
            # TODO: Add error handling
            status_times[self.status_names[status]] = {
                'count': int(count),
                'duration': timedelta(milliseconds=int(msecs))
            }

        return status_times

    def _parse_one_value(self, raw_value):
        """This should never be called on parsers that split values into
        multiple columns.
        """
        raise NotImplementedError

    def parse_values(self, raw_values):
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

        if not raw_values:
            return [u''] * (len(self.statuses) * 2)

        status_times = self._parse_time_in_status(raw_values)
        parsed_values = []
        for status in self.statuses:
            # If there is entry for this status, add on two blank columns.
            # One for the count and one for the duration.
            if status not in status_times:
                parsed_values += [u'', u'']
                continue

            # TODO: Add error handling.
            count = unicode(status_times[status]['count'])
            # Format the duration in decimal days.
            duration = status_times[status]['duration'].total_seconds()
            duration = unicode('%0.2f' % (duration / (60 * 60 * 24)))
            parsed_values += [count, duration]
        return parsed_values
