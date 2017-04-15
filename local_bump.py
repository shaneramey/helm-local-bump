#! /usr/bin/env python

"""local_bump.py: Bump a local Helm Chart.yaml
cd /Users/sramey/git/du/landscape
make -C ../apps/helm-chart-publisher publish_helm && \
helm repo update && \
helm local_bump -f helm-chart-publisher/helm-chart-publisher/helm-chart-publisher.yaml --patch && \
make deploy

Usage:
  local_bump.py -f FILE (--major | --minor | --patch)

Options:
    -f FILE                          Helm Chart.yaml or Landscape yaml
    --bump-level=<bump_level>              Bump Level: (major|minor|patch)
(--left | --right)
    --major   use left-hand side
    --minor  use right-hand side
    --patch  use right-hand side

"""

import docopt
import os
import sys
from ruamel import yaml


def is_chart(yaml_contents):
    if yaml_contents.has_key('name') and yaml_contents.has_key('description') \
            and yaml_contents.has_key('apiVersion') and yaml_contents.has_key('version'):
        return True


def is_landscape(yaml_contents):
    if yaml_contents.has_key('name') and yaml_contents.has_key('release') \
            and yaml_contents['release'].has_key('chart') \
            and yaml_contents['release'].has_key('version'):
        return True


def main():
    args = docopt.docopt(__doc__)

    level_of_bump = args['--major']
    path_to_chart_or_landscape_yaml = args['-f']
    the_yaml = {}
    with open(path_to_chart_or_landscape_yaml, 'r') as stream:
        try:
            the_yaml = yaml.load(stream, Loader=yaml.RoundTripLoader)
        except yaml.YAMLError as exc:
            print(exc)
    # Attempt to parse YAML contents
    if is_chart(the_yaml):
        old_semver = the_yaml['version'].split('.')
    elif is_landscape(the_yaml):
        old_semver = the_yaml['release']['version'].split('.')
    else:
        raise ValueError('Could not parse yaml contents for Helm or Landscape')

    # Bump version
    new_semver = []
    if args['--major']:
        new_semver = [str(int(old_semver[0]) + 1),
                      old_semver[1], old_semver[2]]
    elif args['--minor']:
        new_semver = [old_semver[0], str(
            int(old_semver[1]) + 1), old_semver[2]]
    elif args['--patch']:
        new_semver = [old_semver[0], old_semver[
            1], str(int(old_semver[2]) + 1)]

    new_version = '.'.join(new_semver)

    if is_chart(the_yaml):
        the_yaml['version'] = new_version
    elif is_landscape(the_yaml):
        the_yaml['release']['version'] = new_version
        chart_repo_path = the_yaml['release']['chart'].split(':')[0]
        chart_and_version_path = "{}:{}".format(chart_repo_path, new_version)
        the_yaml['release']['chart'] = chart_and_version_path
    print "bumped to version {}".format('.'.join(new_semver))
    with open(path_to_chart_or_landscape_yaml, 'w') as outfile:
        yaml.dump(the_yaml, outfile, Dumper=yaml.RoundTripDumper)
    outfile.close()

if __name__ == "__main__":
    main()
