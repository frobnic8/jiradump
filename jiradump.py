#!/usr/bin/env python

"""jiradump.py - dump JIRA issues from a filter as delimited plain text"""

__author__ = 'erskin.cherry@opower.com'
__version__ = '1.0.0'

from getpass import getpass, getuser
from jira.client import JIRA
from logging import debug, info, warning, error, getLogger
import argparse
import logging
import sys

# JIRA API configuration parameters.
API_SERVER = 'https://ticket.opower.com'

DEFAULT_OUTPUT_FIELDS = (
    'Key',
    'Project',
    'Issue Type',
    'Summary',
    'Story Points',
    'Assignee',
    'Labels',
    'Priority',
    'Severity',
    'Status',
    'Reporter',
    'Created',
    'Resolution',
    'Resolved',
)

DEFAULT_MAX_RESULTS = 1000

# This dict is used to lookup the log level for a given number of -v options.
_VERBOSE_TO_LOG_LEVEL = {
    None: logging.WARNING,
    0: logging.WARNING,
    1: logging.INFO,
    2: logging.DEBUG
}

# Fields known to contain datetime values that we may want to split into
# separate date and time columns in the output.
DATETIME_FIELDS = (
    'Created',
    'Resolved',
    'Date Reported',
    'Due Date',
    'End Date',
    'Resolved',
)

# TODO: Support that crazy ass 'Time in Status'
#
# Example data:
# u'1_*:*_1_*:*_584742000_*|*_6_*:*_1_*:*_0_*|*_10111_*:*_1_*:*_170163000' + \
# u'_*|*_10112_*:*_1_*:*_352367000'
#
# How to split:
#   [eggs.split('_*:*_') for eggs in spam.split('_*|*_')]
#
# The first part is the status code, the second is the number of times in that
# status, the third is the time in milliseconds.
#
# Ideal output would have multiple columns (two for each status that occurs,
# but only the ones that do occur in the output). One would be times in status
# and the other time in the same status.
#
# Time is probably best in decimal days.
#
# Probably want to filter out time in resolved and closed statuses.


def split_jira_datetime(raw_value, delimiter):
    """Split a JIRA datetime string into separate date and time values.

    e.g. 2013-06-04T15:15:36.000-0400

    """
    return delimiter.join([raw_value[0:10], raw_value[12:19]])


def build_parser():
    """Build a command line argument parser for jiradump."""
    parser = argparse.ArgumentParser(description='dump JIRA issues from a '
                                     'filter as delimited plain text')

    parser.add_argument('-u', '--username', nargs='?', help='specify JIRA '
                        'user account. Defaults to the local username')
    parser.add_argument('-p', '--passfile', nargs='?', help='specify '
                        '*filename* which contains user\'s password. '
                        'Defaults to prompting for password')
    parser.add_argument('-v', '--verbose', action='count', help='increase '
                        'level of feedback output. Use -vv for even more '
                        'detail')
    parser.add_argument('-d', '--delimiter', nargs='?', help='specify output '
                        "column delimiter. Defaults to tab, i.e. '\\t'",
                        default='\t')
    parser.add_argument('-D', '--subdelimiter', nargs='?', help='specify '
                        'delimiter for fields with multiple values. Defaults '
                        "to comma space, i.e. ', '", default=', ')
    parser.add_argument('-o', '--output', nargs='?', help='specify output '
                        'filename. Defaults to standard out')
    parser.add_argument('-m', '--max-results', nargs='?', help='specify '
                        'maximum issues returned. Defaults to %s' %
                        DEFAULT_MAX_RESULTS, default=DEFAULT_MAX_RESULTS)
    parser.add_argument('-f', '--fields', nargs='?', help='specify filename '
                        'of issue fields to dump, one per line. Default '
                        'fields: ' + ', '.join(DEFAULT_OUTPUT_FIELDS),
                        metavar='FIELDS_FILE')
    # TODO: Support this.
    #parser.add_argument('-c', '--command-log', help='append command line '
    #                    'used to output for logging and ease of replay',
    #                    action='store_true')

    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument('--list-fields', help='list all field IDs and names '
                        'known and exit', action='store_true')
    group.add_argument('--list-filters', help='list IDs and names of favorite '
                       'filters, i.e. those findable by name, and exit',
                       action='store_true')
    group.add_argument('filter', metavar='FILTER', nargs='?', help='specifies the '
                        'filter name or ID to dump. Only favorite filters can '
                        'be referenced by name')
    parser.add_argument('--version', action='version',
                        version='%(prog)s ' + __version__)
    return parser


if __name__ == '__main__':
    # Pase the command line arguments.
    args = build_parser().parse_args()

    # Set the logging level based on the verbose option.
    getLogger().setLevel(level=_VERBOSE_TO_LOG_LEVEL.get(args.verbose,
                                                         logging.DEBUG))
    debug('Verbosity level: %s' % args.verbose)


    debug('Building credentials.')
    # Guess the username if possible.
    if not args.username:
        args.username = getuser()

    # Get the password, reading from a file if requested.
    if args.passfile and args.passfile != '-':
        try:
            PASSWORD = open(args.passfile).read().strip()
        except IOError as err:
            error(err)
            error('Failed to read password from file: ' + args.passfile)
            sys.exit(err.get_attr('errno', 1))
    else:
        PASSWORD = getpass()

    # Parse any encoded characters in the delmiter.
    args.delimiter = args.delimiter.decode('string-escape')

    # Configure our JIRA interface.
    options = {'server': API_SERVER}
    jira = JIRA(options=options, basic_auth=(args.username, PASSWORD))
    info('Connecting as %s to %s' % (args.username, API_SERVER))

    # Create a mapping of field names (including custom ones) to field IDs.
    debug('Mapping field names to IDs.')
    # TODO: Added error handling
    field_ids = dict([(field['name'], field['id']) for field in jira.fields()])

    # Create a mapping of filters names (including custom ones) to filter IDs.
    debug('Mapping favorite filter names to IDs.')
    # TODO: Added error handling
    filter_ids = dict([(fav.name, fav.id) for fav in jira.favourite_filters()])

    # Open the output file.
    if args.output:
        info('Writing output to %s', args.output)
        output = open(args.output, 'w')
    else:
        debug('Writing output to standard output.')
        output = sys.stdout

    # If we are just listing the available fields, do so now and exit.
    if args.list_fields:
        # Convert any Unicode values to UTF-8.
        utf8 = []
        for key, value in field_ids.iteritems():
            utf8.append(args.delimiter.join([value, key]).encode('utf-8'))
        output.write('\n'.join(utf8))

        # If we are writing to standard output, add a final newline to be nice.
        if output == sys.stdout:
            output.write('\n')
        sys.exit()

    # If we are just listing the favorite filters, do so now and exit.
    if args.list_filters:
        # Convert any Unicode values to UTF-8.
        utf8 = []
        for key, value in filter_ids.iteritems():
            utf8.append(args.delimiter.join([value, key]).encode('utf-8'))
        output.write('\n'.join(utf8))

        # If we are writing to standard output, add a final newline to be nice.
        if output == sys.stdout:
            output.write('\n')
        sys.exit()

    # Grab the main filter.
    debug('Looking up the issue filter in JIRA.')
    if args.filter in filter_ids:
        info('Found filter %s in favorites as ID %s.' %
             (filter_ids[args.filter], args.filter))
        dump_filter = jira.filter(filter_ids[args.filter])
    else:
        # TODO: Added error handling
        info('Looking up filter using %s as an ID.' % args.filter)
        dump_filter = jira.filter(args.filter)

    # Grab the issues from the filter.
    info('Retrieving up to %s issues from filter %s (ID %s).' %
         (args.max_results, dump_filter.name, dump_filter.id))
    issues = jira.search_issues(dump_filter.jql, maxResults=args.max_results)

    # Create the list of fields we will dump.
    if args.fields:
        output_fields = []
        with open(args.fields) as fields_file:
            for field in fields_file:
                field = field.strip()
                if field:
                    output_fields.append(field)
    else:
        output_fields = DEFAULT_OUTPUT_FIELDS
    debug('Output fields: ' + ', '.join(output_fields))

    # TODO: Handle splitting datetime fields.
    #if args.split_datetime:

    # Create a header row for the output.
    # Leave off the newline so we can make sure we don't add a final blank
    # line when sending output to a file.
    headers = []
    # Walk the list to check for any headers we need to process.
    # TODO: There has GOT to be a less ugly way to do this.
    for field in output_fields:
        # Split any datetime headers in two.
        if field in DATETIME_FIELDS:
            headers.append('Date %s%sTime %s' % (field, args.delimiter, field))
        else:
            headers.append(field)
    output.write(args.delimiter.join(headers))

    # Write out the summary for each issue.
    for issue in issues:
        # Dirty hack to make the "key" attribute available at the same
        # level as all the other fields.
        issue.fields.issuekey = issue.key

        # Look up the values for each field.
        values = []
        for field in output_fields:
            value = getattr(issue.fields, field_ids[field], '')

            # If this field holds multiple values, convert them into a single
            # string.
            if not isinstance(value, basestring):
                try:
                    value = args.subdelimiter.join([unicode(val) for val in value])
                except TypeError:
                    pass

            # Split any datetime values in two.
            if field in DATETIME_FIELDS:
                if value:
                    value = split_jira_datetime(value, args.delimiter)
                else:
                    value = args.delimiter

            # And convert any Unicode to UTF-8.
            values.append(unicode(value).encode('utf-8'))

        # We add the newline before each new row so we don't end with a
        # final blank line when sending output to a file.
        output.write('\n' + args.delimiter.join(values))

    # TODO: Opitionally add the command line used to produce the outoput.

    # If we are writing to standard output, add a final newline to be nice.
    if output == sys.stdout:
        output.write('\n')
