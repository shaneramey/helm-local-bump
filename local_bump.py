#! /usr/bin/env python

"""local_bump.py: Bump a local Helm Chart.yaml
Use case: deploy updated Helm chart and bump the landscape version
```
cd /Users/sramey/git/du/landscape
make -C ../apps/helm-chart-publisher publish_helm && \
helm repo update && \
helm local_bump -f helm-chart-publisher/helm-chart-publisher/helm-chart-publisher.yaml --patch && \
make deploy
```

Usage:
  local_bump.py -f FILE (--bump-level=BUMP_LEVEL | --bump-version=BUMP_VERSION)

Options:
    -f FILE				Helm Chart.yaml or Landscape yaml
    --bump-level=BUMP_LEVEL		Bump Level: (major|minor|patch)
    --bump-version=BUMP_VERSION		Bump Version: manually set version

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


def is_semver_format(dotted_string):
    semver_list = dotted_string.split('.')
    if len(semver_list) == 3 \
        and type(int(semver_list[0])) is int \
        and type(int(semver_list[1])) is int \
        and type(int(semver_list[2])) is int:
        return True
    else:
        return False


def main():
    args = docopt.docopt(__doc__)

    level_of_bump = args['--bump-level']
    manual_version_of_bump = args['--bump-version']
    path_to_chart_or_landscape_yaml = args['-f']

    # Read the YAML file we're bumping
    the_yaml = {}
    with open(path_to_chart_or_landscape_yaml, 'r') as stream:
        try:
            the_yaml = yaml.load(stream, Loader=yaml.RoundTripLoader)
        except yaml.YAMLError as exc:
            print(exc)
    # Attempt to parse YAML contents as Chart or Landscape file
    if is_chart(the_yaml):
        old_version = the_yaml['version']
    elif is_landscape(the_yaml):
        old_version = the_yaml['release']['version']
    else:
        print "Oops. Couldnt parse the yaml:"
	print the_yaml
        raise ValueError('Could not parse yaml contents for Helm or Landscape')

    if not is_semver_format(old_version):
        print "Invalid format of parsed semver: {}".format(old_version)
        sys.exit(4)
    old_semver = old_version.split('.')

    # Bump version
    new_version = []
    # if --bump-level is passed
    if level_of_bump is not None:
        if level_of_bump == 'major':
            new_semver = [str(int(old_semver[0]) + 1),
                          old_semver[1], old_semver[2]]
        elif level_of_bump == 'minor':
            new_semver = [old_semver[0], str(
                int(old_semver[1]) + 1), old_semver[2]]
        elif level_of_bump == 'patch':
            new_semver = [old_semver[0], old_semver[
                1], str(int(old_semver[2]) + 1)]
        else:
            print "Invalid bump level: '{}'. Please specify one of major, minor, patch".format(level_of_bump)
        new_version = '.'.join(new_semver)

    if manual_version_of_bump is not None:
        if is_semver_format(manual_version_of_bump):
            new_version = manual_version_of_bump
        else:
            print "Invalid format of parsed semver: {}".format(old_version)

    if not is_semver_format(new_version):
        print "Invalid format of generated semver: {}".format(new_version)
        sys.exit(4)

    if is_chart(the_yaml):
        the_yaml['version'] = new_version
    elif is_landscape(the_yaml):
        the_yaml['release']['version'] = new_version
        chart_repo_path = the_yaml['release']['chart'].split(':')[0]
        chart_and_version_path = "{}:{}".format(chart_repo_path, new_version)
        the_yaml['release']['chart'] = chart_and_version_path
    print "bumped to version {}".format(new_version)
    with open(path_to_chart_or_landscape_yaml, 'w') as outfile:
        yaml.dump(the_yaml, outfile, Dumper=yaml.RoundTripDumper)
    outfile.close()

if __name__ == "__main__":
    main()
