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
  local_bump.py [-q] -f FILE (--bump-level=BUMP_LEVEL | --bump-version=BUMP_VERSION)

Options:
    -q                                  Quiet mode. Output only new version
    -f FILE				Helm Chart.yaml or Landscape yaml
    --bump-level=BUMP_LEVEL		Bump Level: (major|minor|patch)
    --bump-version=BUMP_VERSION		Bump Version: manually set version

"""

import docopt
import os
import sys
import re
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
    major_version = semver_list[0]
    minor_version = semver_list[1]
    patch_version_and_metadata = semver_list[2]
    patch_version, metadata_version = re.match("^([0-9])+(.*)", patch_version_and_metadata).groups()

    if type(int(major_version)) is int \
        and type(int(minor_version)) is int \
        and type(int(patch_version)) is int:
        return True
    else:
        return False

def bump_version(original_version, bump_level):
    """Returns a bumped version
    Arguments:
        original_version: a str containing the current version

    Returns:
        Bumped version str
    """
    old_semver = original_version.split('.')
    current_major_version = int(old_semver[0])
    current_minor_version = int(old_semver[1])
    # parse metadata out of semver string for incrementing patch level
    current_patch_version_and_metadata = old_semver[2]
    current_patch_version_str, version_metadata = re.match("^([0-9]+)(.*)",
                                        current_patch_version_and_metadata
                                        ).groups()
    current_patch_version = int(current_patch_version_str)

    # increment a bump level by 1 and return result
    if bump_level == 'major':
        return compose_semver(current_major_version + 1,
                                    current_minor_version,
                                    current_patch_version,
                                    version_metadata)
    elif bump_level == 'minor':
        return compose_semver(current_major_version,
                                    current_minor_version + 1,
                                    current_patch_version,
                                    version_metadata)
    elif bump_level == 'patch':
        return compose_semver(current_major_version,
                                    current_minor_version,
                                    current_patch_version + 1,
                                    version_metadata)
    else:
        raise ValueError("Invalid bump level: '{}'. Please specify one of major, minor, patch".format(bump_level))


def compose_semver(major, minor, patch, metadata):
    return "{0}.{1}.{2}{3}".format(
                        major,
                        minor,
                        patch,
                        metadata)

def main():
    args = docopt.docopt(__doc__)

    level_of_bump = args['--bump-level']
    manual_version_of_bump = args['--bump-version']
    path_to_chart_or_landscape_yaml = args['-f']
    quiet_mode = args['-q']

    # Read the YAML file we're bumping
    the_yaml = {}
    with open(path_to_chart_or_landscape_yaml, 'r') as stream:
        try:
            the_yaml = yaml.load(stream, Loader=yaml.RoundTripLoader)
        except yaml.YAMLError as exc:
            print(exc)
    # Attempt to parse YAML contents as Chart or Landscape file
    if is_chart(the_yaml):
        current_version = the_yaml['version']
    elif is_landscape(the_yaml):
        current_version = the_yaml['release']['version']
    else:
        raise ValueError("Couldn\'t parse as Helm Chart or landscaper yaml: {0}".format(the_yaml))

    if not is_semver_format(current_version):
        print "Invalid format of parsed semver: {}".format(current_version)
        sys.exit(4)

    new_semver = manual_version_of_bump
    if level_of_bump:
        new_semver = bump_version(current_version, level_of_bump)

    if not is_semver_format(new_semver):
        raise ValueError("Invalid format of generated semver: {}".format(new_semver))

    # Format of landscaper and helm charts yaml differs
    if is_chart(the_yaml):
        the_yaml['version'] = new_semver
    elif is_landscape(the_yaml):
        the_yaml['release']['version'] = new_semver
        chart_repo_path = the_yaml['release']['chart'].split(':')[0]
        chart_and_version_path = "{}:{}".format(chart_repo_path, new_semver)
        the_yaml['release']['chart'] = chart_and_version_path
    if quiet_mode:
        print new_semver
    else:
        print "Bumped to version {}".format(new_semver)
    with open(path_to_chart_or_landscape_yaml, 'w') as outfile:
        yaml.dump(the_yaml, outfile, Dumper=yaml.RoundTripDumper)
    outfile.close()

if __name__ == "__main__":
    main()
