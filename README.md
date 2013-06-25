jiradump
========

dump JIRA issues from a filter as delimited plain text

Installation
------------

This uses jira-python to make talking to the JIRA REST API easier. The bad news
is, jira-python has a few dependencies, and I had to add a minor tweak or two
as well, so it can be more of a pain to install than it should be.

This /should/ get you what you need:

    pip install jira-python

Except for my (currently pending as a pull request) fork:

https://bitbucket.org/frobnic8/jira-python/overview

I've just been throwing my fork into jiradump folder and letting the local jira
package override the system default for now while I hack around.

Seriously, if you need this right now, just come ping me and I'll hook you up.
Once Opower gets a nice local PyPI server and I get my act together and package
this properly, it'll get a lot easier.


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

Known Bugs
----------
Rendering the 'Time in Status' field is current a dirty, dirty hack that ignores
any settings for subdelimiter and has a fixed sub-subdelimiter of ':'. I need to
replace it with a proper parsing object infrastructure at some point.
