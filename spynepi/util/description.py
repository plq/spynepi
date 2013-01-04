
#
# Shamelessly ripped off from:
#
# https://bitbucket.org/loewis/pypi/src/b3c267d4ca696ca94427cff1e832238d0bf6be5f/description_utils.py?at=default
#


import sys
import StringIO
import cgi
import urlparse

import docutils.utils # workaround that makes the next import work.

from docutils import io
from docutils import readers
from docutils.core import Publisher
from docutils.core import publish_doctree
from docutils.transforms import TransformError


def trim_docstring(text):
    """
    Trim indentation and blank lines from docstring text & return it.

    See PEP 257.
    """
    if not text:
        return text
    # Convert tabs to spaces (following the normal Python rules)
    # and split into a list of lines:
    lines = text.expandtabs().splitlines()
    # Determine minimum indentation (first line doesn't count):
    indent = sys.maxint
    for line in lines[1:]:
        stripped = line.lstrip()
        if stripped:
            indent = min(indent, len(line) - len(stripped))
    # Remove indentation (first line is special):
    trimmed = [lines[0].strip()]
    if indent < sys.maxint:
        for line in lines[1:]:
            trimmed.append(line[indent:].rstrip())
    # Strip off trailing and leading blank lines:
    while trimmed and not trimmed[-1]:
        trimmed.pop()
    while trimmed and not trimmed[0]:
        trimmed.pop(0)
    # Return a single string:
    return '\n'.join(trimmed)


ALLOWED_SCHEMES = '''file ftp gopher hdl http https imap mailto mms news nntp
prospero rsync rtsp rtspu sftp shttp sip sips snews svn svn+ssh telnet
wais'''.split()


def process_description(source, output_encoding='unicode'):
    """Given an source string, returns an HTML fragment as a string.

    The return value is the contents of the <body> tag.

    Parameters:

    - `source`: A multi-line text string; required.
    - `output_encoding`: The desired encoding of the output.  If a Unicode
      string is desired, use the default value of "unicode" .
    """
    # Dedent all lines of `source`.
    source = trim_docstring(source)

    settings_overrides={
        'raw_enabled': 0,  # no raw HTML code
        'file_insertion_enabled': 0,  # no file/URL access
        'halt_level': 2,  # at warnings or errors, raise an exception
        'report_level': 5,  # never report problems with the reST code
        }

    # capture publishing errors, they go to stderr
    old_stderr = sys.stderr
    sys.stderr = s = StringIO.StringIO()
    parts = None

    try:
        # Convert reStructuredText to HTML using Docutils.
        document = publish_doctree(source=source,
            settings_overrides=settings_overrides)

        for node in document.traverse():
            if node.tagname == '#text':
                continue
            if node.hasattr('refuri'):
                uri = node['refuri']
            elif node.hasattr('uri'):
                uri = node['uri']
            else:
                continue
            o = urlparse.urlparse(uri)
            if o.scheme not in ALLOWED_SCHEMES:
                raise TransformError('link scheme not allowed')

        # now turn the transformed document into HTML
        reader = readers.doctree.Reader(parser_name='null')
        pub = Publisher(reader, source=io.DocTreeInput(document),
            destination_class=io.StringOutput)
        pub.set_writer('html')
        pub.process_programmatic_settings(None, settings_overrides, None)
        pub.set_destination(None, None)
        pub.publish()
        parts = pub.writer.parts

    except:
        pass

    sys.stderr = old_stderr

    # original text if publishing errors occur
    if parts is None or len(s.getvalue()) > 0:
        output = "".join('<PRE>\n' + cgi.escape(source) + '</PRE>')
    else:
        output = parts['body']

    if output_encoding != 'unicode':
        output = output.encode(output_encoding)

    return output
