jiradump
========

Dump JIRA issues from a filter, including custom fields, as delimited text

Installation
------------

The jiradump tool is now available in a nice wheel package.

If that doesn't mean anything to you and you've never installed python
stuff before, these will probably be the terminal commands you want to run:

    easy_install pip
    pip install --upgrade setuptools
    pip install wheel
    pip install git+https://github.com/frobnic8/jiradump

If it dies on just the last command, you probably need to install git.
On a Mac, if you don't have it you will get a prompt to install it.
Afterwards, you'll then need to run the last command again.

If you are running Windows, you are probably going to have a bad time.
Sorry about that.

If the first command fails, and this is your personal computer, you can
try it again with a little more powerful permissions: (This will prompt
you for your login password)

    sudo -H easy_install pip
    sudo -H pip install --upgrade setuptools
    sudo -H pip install git+https://github.com/frobnic8/jiradump

To test your installation, run:

    jiradump --help

You probably only use one JIRA server, and probably don't want to type it
in every time. You can set the JIRA_SERVER environment variable and jiradump
will default to that. Something like this in your .bash_profile should work:

    export JIRA_SERVER=https://jira.example.com

Usage
-----

Like any respectable command line tool, jiradump supports -h for help.

You get three features:

* List the known set of fields, and IDs
* List your favorite filters, and IDs
* List the known set of issues status names and IDs
* Dump issues for a filter


### Quick Example

List the filters you have favorited in JIRA:

    jiradump --list-filters

    11681   My Unresolved Assigned Tickets
    13109   My Unresolved Reporting Requests
    13187   My Unresolved Past Iteration Tickets
    17196   CS Fires and Maintenance
    17447   Critical Client Issues

Pick a filter (name or number will work, but use quotes if you use the name and
it has spaces in it!) and dump it out:

    jiradump "Critical Client Issues" > ~/Documents/cci_ticket_dump.txt

Then just open the file in a spreadsheet program.

### Detailed Usage

Because you are likely running this on your local laptop, you'll probably want
the -u option to specify your username.

List Fields:

    jiradump --list-fields

This is useful if you want to make a file to tell jiradump what specific fields
you want to include in the extract.

List Filters:

    jiradump --list-filters

You can dump any JIRA filter if you know the ID, but you can only look up the
ID for filters in your favorites. This lists your favorite filters and their
IDs for reference.

List Statuses:

    jiradump --list-statuses

This just lists the statues available in JIRA. It's admittedly less useful
outside of debugging stuff.

Dump Issues:

    jiradump FILTER_NAME_OR_ID

Dumps the default set of fields with the default delimiter for up to the
default number of issues to standard output.

Here's the full usage. Note that options like delimiter and output file name
work with list filters and list fields as well as the standard issue dump.

    usage: jiradump [-h] [-u USERNAME] [-p PASSFILE] [-j JIRA] [-v]
                    [-d [DELIMITER]] [-D [SUBDELIMITER]] [-o [OUTPUT]]
                    [-m [MAX_RESULTS]] [-f [FIELDS_FILE]] [--list-fields]
                    [--list-filters] [--list-statuses] [--version]
                    [FILTER]

    dump JIRA issues from a filter as delimited plain text

    positional arguments:
      FILTER                specifies the filter name or ID to dump. Only favorite
                            filters can be referenced by name

    optional arguments:
      -h, --help            show this help message and exit
      -u USERNAME, --username USERNAME
                            specify JIRA user account. Defaults to the local
                            username
      -p PASSFILE, --passfile PASSFILE
                            specify *filename* which contains user's password.
                            Defaults to prompting for password
      -j JIRA, --jira JIRA  specify JIRA server. Defaults to
                            https://jira.atlassian.com
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
