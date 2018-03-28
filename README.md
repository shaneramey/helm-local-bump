# Helm plugin to parse Chart.yaml and increment the version number

NOTE: This plugin isn't being actively developed. https://github.com/mbenabda/helm-local-chart-version is a great alternative.

Installation:
```
helm plugin install https://github.com/shaneramey/helm-local-bump
```

Usage:
```
helm local_bump [-q] path/to/Chart.yaml --bump-level=(major|minor|patch)

helm local_bump [-q] path/to/Chart.yaml --bump-version=1.2.3+asdfg
```
