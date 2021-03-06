#!/usr/bin/env python

"""jiradump.py - dump JIRA issues from a filter as delimited text"""

__author__ = 'erskin@eldritch.org'
__version__ = '1.1.2'

from getpass import getpass, getuser
from jira.client import JIRA
from logging import debug, info, error, getLogger
from jiradump.parsers import BasicFieldParser, DateTimeFieldParser, \
    SecondsDurationParser, TimeInStatusFieldParser
import argparse
import jira.resources
import logging
import sys
import os

# Environment variables, in order of precendence, to check for a username.
USER_ENVS = ['JIRADUMP_USER']

# JIRA API configuration parameters.
API_SERVER_ENVS = ['JIRA_URL']
DEFAULT_API_SERVER = 'https://jira.atlassian.com'

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
FIELD_PARSERS = {
    'Created': DateTimeFieldParser,
    'Resolved': DateTimeFieldParser,
    'Date Reported': DateTimeFieldParser,
    'Due Date': DateTimeFieldParser,
    'End Date': DateTimeFieldParser,
    'Time in Status': TimeInStatusFieldParser,
    'Days since last comment': SecondsDurationParser,
}


def build_parser():
    """Build a command line argument parser for jiradump."""
    parser = argparse.ArgumentParser(description='dump JIRA issues from a '
                                     'filter as delimited plain text')

    # TODO: Display default fields in help.

    parser.add_argument('-u', '--username', nargs=1, help='specify JIRA '
                        'user account. Defaults to the local username')
    parser.add_argument('-p', '--passfile', nargs=1, help='specify '
                        '*filename* which contains user\'s password. '
                        'Defaults to prompting for password')
    parser.add_argument('-j', '--jira', nargs=1, help='specify JIRA '
                        'server. Defaults to ' + get_jira_server())
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

    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument('--list-fields', help='list all field IDs and names '
                       'known and exit', action='store_true')
    group.add_argument('--list-filters', help='list IDs and names of favorite '
                       'filters, i.e. those findable by name, and exit',
                       action='store_true')
    group.add_argument('--list-statuses', help='list all status IDs and names '
                       'known and exit', action='store_true')
    group.add_argument('filter', metavar='FILTER', nargs='?',
                       help='specifies the filter name or ID to dump. Only '
                       'favorite filters can be referenced by name')
    parser.add_argument('--version', action='version',
                        version='%(prog)s ' + __version__)
    return parser


def list_items(items, delimiter, output, flip=False):
    """Write the item's keys and values to the output."""
    # Convert any Unicode values to UTF-8.
    utf8 = []
    for key, value in items.iteritems():
        if flip:
            key, value = value, key
        utf8.append(delimiter.join([key, value]).encode('utf-8'))
    output.write('\n'.join(utf8))

    # If we are writing to standard output, add a final newline to be nice.
    if output == sys.stdout:
        output.write('\n')
    sys.exit()


def get_jira_server():
    for env in API_SERVER_ENVS:
        if env in os.environ and os.environ[env]:
            return os.environ[env]
    return DEFAULT_API_SERVER


def get_jiradump_user():
    """Guess the username from known environment variables or the system."""
    for env in USER_ENVS:
        if env in os.environ and os.environ[env]:
            return os.environ[env]
    return getuser()


def main():
    """Parse arguments and retrieve filters, fields, status, or dump issues."""
    # Parse the command line arguments.
    args = build_parser().parse_args()

    # Set the logging level based on the verbose option.
    getLogger().setLevel(level=_VERBOSE_TO_LOG_LEVEL.get(args.verbose,
                                                         logging.DEBUG))
    debug('Verbosity level: %s' % args.verbose)

    debug('Building credentials.')
    # Guess the username if possible.
    if args.username:
        args.username = args.username[0]
    else:
        args.username = get_jiradump_user()

    # Get the password, reading from a file if requested.
    if args.passfile and args.passfile[0] != '-':
        try:
            password = open(args.passfile[0]).read().strip()
        except IOError as err:
            error(err)
            error('Failed to read password from file: ' + args.passfile[0])
            sys.exit(getattr(err, 'errno', 1))
    else:
        password = getpass()

    # Determine the JIRA server to connect to.
    if args.jira:
        args.jira = args.jira[0]
    else:
        args.jira = get_jira_server()
    # Assume HTTPS if no URI method is given
    if '://' not in args.jira:
        args.jira = 'https://' + args.jira

    # Parse any encoded characters in the delmiter.
    args.delimiter = args.delimiter.decode('string-escape')

    # Setup JIRA and file connections.

    # Configure our JIRA interface.
    options = {'server': args.jira}
    jira = JIRA(options=options, basic_auth=(args.username, password))
    info('Connecting as %s to %s' % (args.username, args.jira))

    # Create a mapping of field names (including custom ones) to field IDs.
    debug('Mapping field names to IDs.')
    # TODO: Add error handling
    field_ids = dict([(field['name'], field['id']) for field in jira.fields()])

    # Create a mapping of filters names (including custom ones) to filter IDs.
    debug('Mapping favorite filter names to IDs.')
    # TODO: Add error handling
    filter_ids = dict([(fav.name, fav.id) for fav in jira.favourite_filters()])

    # Open the output file.
    if args.output:
        info('Writing output to %s', args.output)
        output = open(args.output, 'w')
    else:
        debug('Writing output to standard output.')
        output = sys.stdout

    # TODO: Optionally add the command line used to produce the output.

    # If we are just listing the available statuses, do so now and exit.
    if args.list_statuses:
        # Create a mapping of status IDs to names (including custom statuses).
        debug('Mapping status IDs to names.')
        # TODO: Add error handling
        status_names = dict([(status.id, status.name)
                             for status in jira.statuses()])

        list_items(status_names, args.delimiter, output)
        sys.exit()

    # If we are just listing the available fields, do so now and exit.
    if args.list_fields:
        list_items(field_ids, args.delimiter, output, flip=True)
        sys.exit()

    # If we are just listing the favorite filters, do so now and exit.
    if args.list_filters:
        list_items(filter_ids, args.delimiter, output, flip=True)
        sys.exit()

    # Parse the filter issues and output.

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
        input_fields = []
        with open(args.fields) as fields_file:
            for field in fields_file:
                field = field.strip()
                if field:
                    input_fields.append(field)
    else:
        input_fields = DEFAULT_OUTPUT_FIELDS
    debug('Input fields from filter: ' + ', '.join(input_fields))

    # Ensure all the fields we want to use are valid.
    unknown_fields = set(input_fields) - set(field_ids.keys())
    if unknown_fields:
        raise ValueError('Unknown field(s): ' + ', '.join(unknown_fields))

    field_parsers = {}

    for field in input_fields:
        Parser = FIELD_PARSERS.get(field, BasicFieldParser)
        field_parsers[field] = Parser(field, issues, jira, args.subdelimiter)

    # Create a header row for the output.
    # First handle any header splitting.
    output_fields = []
    for field in input_fields:
        output_fields += field_parsers[field].headers()
    debug('Output columns: ' + ', '.join(output_fields))

    # Leave off the newline so we can make sure we don't add a final blank
    # line when sending output to a file.
    output.write(args.delimiter.join(output_fields))

    # Write out the summary for each issue.
    for issue in issues:
        # Dirty hack to make the "key" attribute available at the same
        # level as all the other fields.
        issue.fields.issuekey = issue.key

        # Look up and parse the individual values for each field in this issue.
        issue_values = []

        for field in input_fields:
            # Grab the values.
            field_values = getattr(issue.fields, field_ids[field], u'')
            # Parse the values.
            field_values = field_parsers[field].parse_values(field_values)

            # Convert from Unicode to UTF-8.
            issue_values += [value.encode('utf-8') for value in field_values]

        # We add the newline before each new row so we don't end with a
        # final blank line when sending output to a file.
        output.write('\n' + args.delimiter.join(issue_values))

    # If we are writing to standard output, add a final newline to be nice.
    if output == sys.stdout:
        output.write('\n')
