# VimJolts

VimJolts the Vim Package Management

<http://vimjolts.appspot.com/>

## Commands

Search plugins which names begin with `fuzzy`:

    $ jolt search fuzzy

Install a Vim plugin `quickrun` under the global environment, with installing dependent plugins at the same time.

    $ sudo jolt install quickrun

Install a Vim plugin `quickrun` under your home directory.

    $ jolt install quickrun

Uninstall as well.

    $ sudo jolt uninstall quickrun
    $ jolt uninstall quickrun

Update all old plugins

    $ sudo jolt update

## Design philosophy

* Automatic dependency resolution
* Uninstallable
* Searchable

## Development

* No spec, no commit
