jiradump
========

Dump JIRA issues from a filter, including custom fields, as delimited text

Installation
------------

The sfs tool is now available in a nice egg package.

If you've never installed python stuff before, this will probably be the
terminal commands you want to run: (This will prompt you for your login
password)

    sudo easy_install pip
    sudo pip install --upgrade setuptools
    sudo pip install git+https://github.va.opower.it/erskin-cherry/jiradump

To test your installation, run:

    jiradump --help

If you are still having problems, just let Erskin know and he'll help you out.

Usage
-----

Like any respectable command line tool, jiradump supports -h for help.

You get three features:

* List the known set of fields, and IDs
* List your favorite filters, and IDs
* List the known set of issues status names and IDs
* Dump issues for a filter

Because you are likely running this on your local laptop, you'll probably want
the -u option to specify your username.

List Fields:

    jiradump.py --list-fields

This is useful if you want to make a file to tell jiradump what specific fields
you want to include in the extract.

List Filters:

    jiradump.py --list-filters

You can dump any JIRA filter if you know the ID, but you can only look up the
ID for filters in your favorites. This lists your favorite filters and their
IDs for reference.

List Statuses:

    jiradump.py --list-statuses

This just lists the statues available in JIRA. It's admittedly less useful
outside of debugging stuff.

Dump Issues:

    jiradump FILTER_NAME_OR_ID

Dumps the default set of fields with the default delimiter for up to the
default number of issues to standard output.

Here's the full usage. Note that options like delimiter and output file name
work with list filters and list fields as well as the standard issue dump.

    usage: jiradump.py [-h] [-u [USERNAME]] [-p [PASSFILE]] [-v] [-d [DELIMITER]]
                       [-D [SUBDELIMITER]] [-o [OUTPUT]] [-m [MAX_RESULTS]]
                       [-f [FIELDS_FILE]] [--list-fields] [--list-filters]
                       [--list-statuses] [--version]
                       [FILTER]

    dump JIRA issues from a filter as delimited plain text

    positional arguments:
      FILTER                specifies the filter name or ID to dump. Only favorite
                            filters can be referenced by name

    optional arguments:
      -h, --help            show this help message and exit
      -u [USERNAME], --username [USERNAME]
                            specify JIRA user account. Defaults to the local
                            username
      -p [PASSFILE], --passfile [PASSFILE]
                            specify *filename* which contains user's password.
                            Defaults to prompting for password
      -v, --verbose         increase level of feedback output. Use -vv for even
                            more detail
      -d [DELIMITER], --delimiter [DELIMITER]
                            specify output column delimiter. Defaults to tab, i.e.
                            '\t'
      -D [SUBDELIMITER], --subdelimiter [SUBDELIMITER]
                            specify delimiter for fields with multiple values.
                            Defaults to comma space, i.e. ', '
      -o [OUTPUT], --output [OUTPUT]
                            specify output filename. Defaults to standard out
      -m [MAX_RESULTS], --max-results [MAX_RESULTS]
                            specify maximum issues returned. Defaults to 1000
      -f [FIELDS_FILE], --fields [FIELDS_FILE]
                            specify filename of issue fields to dump, one per
                            line. Default fields: Key, Project, Issue Type,
                            Summary, Story Points, Assignee, Labels, Priority,
                            Severity, Status, Reporter, Created, Resolution,
                            Resolved
      --list-fields         list all field IDs and names known and exit
      --list-filters        list IDs and names of favorite filters, i.e. those
                            findable by name, and exit
      --list-statuses       list all status IDs and names known and exit
      --version             show program's version number and exit
