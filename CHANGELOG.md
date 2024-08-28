# Change Log

All notable changes to this project will be documented in this file.
This project adheres to [Semantic Versioning](http://semver.org/).
This project adheres to [CHANGELOG](http://keepachangelog.com/).

## [Unreleased]

## [1.6.0] - 2024-08-28

### Fixed

- Add proper error handling for cases when SOA record is None
- `random.randint` requires `int` arguments ([#44](https://github.com/mschwager/fierce/issues/44))

### Added

- Official Python 3.11 support
- Official Python 3.12 support

### Removed

- Official Python 3.6 support
- Official Python 3.7 support

## [1.5.0] - 2021-12-05

### Added

- Official Python 3.9 support
- Official Python 3.10 support

### Changed

- Improved various error handling

### Removed

- Official Python 3.5 support

## [1.4.0] - 2019-11-07

### Added

- Official Python 3.8 support
- The --tcp flag to use TCP instead of UDP DNS queries

### Removed

- Official Python 3.4 support, it's EOL

## [1.3.0] - 2019-05-15

### Changed

- Print out all A records for wildcard, not just first one

### Added

- Filter out subdomains with an A record matching a wildcard A record
- Official Python 3.7 support

### Fixed

- Prevent out of bounds error when expanding IPs near 0.0.0.0 or 255.255.255.255

## [1.2.2] - 2018-04-24

### Changed

- Python 3 is now a requirement when installing via setup.py (including pip)
- The README markdown is now included in the package's long description

## [1.2.1] - 2018-03-01

### Changed

- Nearby IP reverse queries are now multithread, which improves performance significantly
- Updated development dependencies
- Subdomain lists use package_data instead of data_files

### Added

- Gracefully handle users exiting the script with Ctrl+C
- Gracefully handle incorrect file or IP range arguments

### Removed

- Official Python 3.3 support, it's EOL

## [1.2.0] - 2017-05-07

### Added

- Official Python 3.6 support

### Fixed

- Handling of subdomains specified that are actually FQDNs
- Gracefully handling timeouts when querying nameservers
- Gracefully handling timeouts when querying zone transfers

## [1.1.5] - 2017-01-08

### Fixed

- Fixed bug with CNAME records pointing to an A record without an associated IP
- Fixed bug with connections being closed by remote peer

## [1.1.4] - 2016-08-30

### Fixed

- Undo a PR that was breaking everything

## [1.1.3] - 2016-08-30

### Fixed

- Fixed a subdomain concatenation bug

## [1.1.2] - 2016-08-15

### Changed

- PyPI is absolutely ridiculous and needs a new version to upload the same package

## [1.1.1] - 2016-08-11

### Changed

- Better error handling when making network connections
- PEP8 formatting

## [1.1.0] - 2016-05-16

### Added

- Intelligent subdomain file searching
- PyPI classifiers

### Changed

- Using more modern setuptools instead of distutils
- Small README improvements

## [1.0.0] - 2016-05-08

### Added

- Initial release of Fierce
