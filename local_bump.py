#! /usr/bin/env python

"""local_bump.py: Bump a local Helm Chart.yaml

Usage:
  local_bump.py path/to/Chart.yaml [major|minor|patch]

"""

import os
import sys
from ruamel import yaml

def print_usage():
    print "Usage: helm local_bump path/to/Chart.yaml [major|minor|patch]"


def main():
    if not len(sys.argv) == 3:
        print_usage()
        sys.exit(1)
    path_to_chart_yaml = sys.argv[1]
    bump_level = sys.argv[2]
    chart_yaml = {}
    with open(path_to_chart_yaml, 'r') as stream:
        try:
            chart_yaml = yaml.load(stream, Loader=yaml.RoundTripLoader)
        except yaml.YAMLError as exc:
            print(exc)
    old_semver = chart_yaml['version'].split('.')
    print "old version: {}".format('.'.join(old_semver))
    new_semver = []
    if bump_level == 'major':
        new_semver = [str(int(old_semver[0]) + 1),
                      old_semver[1], old_semver[2]]
    elif bump_level == 'minor':
        new_semver = [old_semver[0], str(
            int(old_semver[1]) + 1), old_semver[2]]
    elif bump_level == 'patch':
        new_semver = [old_semver[0], old_semver[
            1], str(int(old_semver[2]) + 1)]
    else:
        print_usage()
        sys.exit(2)
    new_version = '.'.join(new_semver)
    chart_yaml['version'] = new_version
    print "new version: {}".format('.'.join(new_semver))
    with open(path_to_chart_yaml, 'w') as outfile:
        yaml.dump(chart_yaml, outfile, Dumper=yaml.RoundTripDumper)
    outfile.close()
    
if __name__ == "__main__":
    main()
