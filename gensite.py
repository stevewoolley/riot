#!/usr/bin/env python

import jinja2
import argparse
import os

if __name__ == "__main__":
    # parse arguments
    parser = argparse.ArgumentParser()
    parser.add_argument("templates", nargs='+', help="templates to parse")
    parser.add_argument("-x", "--extension", help="file extension to export", required=True)
    args = parser.parse_args()

    TEMPLATE_LOADER = jinja2.FileSystemLoader(searchpath="templates")
    TEMPLATE_ENV = jinja2.Environment(loader=TEMPLATE_LOADER)

    for t in args.templates:
        filename, file_extension = os.path.splitext(t)
        template = TEMPLATE_ENV.get_template(t)
        outputText = template.render()
        template.stream().dump("{}.{}".format(filename, args.extension))
        print "input: {}.{} ouput: {}.{}".format(filename, file_extension, filename, args.extension)
