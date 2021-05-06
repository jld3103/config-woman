# config-woman

_Why be a config man'ager, when you can be a config woman'ager?_

## Storyline

There is no real story, but I was using https://github.com/CyberShadow/aconfmgr and didn't like, that it was so slow,
and I felt uncomfortable in the way how it worked. It just wasn't _fancy_ enough for me.  
I decided to create this, because I wanted to make things easier, more straight forward and because I can.  
The main features I want:

- [x] System package management
- [x] System config file management
- [x] High speed operation
- [x] Portability to other package managers than `pacman`: `apt` already supported, more will follow
- [ ] Secret management so your valuable access keys and passwords won't be leaked via the config state
- [x] User dotfile management

## Usage

Create a venv using `python3 -m venv ./venv` and then activate it via `source venv/bin/activate`. Install the
dependencies using `pip3 install -r requirements.txt`.

### System mode

#### Save system state to config

The default preset for system mode is named `default_system`:

```
python3 main.py system save [preset]
```

Now you have `[preset].yaml`, `[preset]_missing.yaml` and `[preset]_redundant.yaml` inside `~/.config/config-woman/`.
Don't worry if the last is missing, you're either on the first run or already configured your config correctly.

The config state you want to have will live in `[preset].yaml`, while everything that lives in the system, but isn't
listed in your config yet, lives in `[preset]_missing.yaml`.

You should now start sorting packages and files from `[preset]_missing.yaml` to `[preset].yaml` or remove them from your
system. You will very likely want to exclude files and directories from the config. To do that just list them in
the `exclude_files` field of `[preset].yaml`. You probably should start with the excluding, because that will already
remove a lot of files that you probably don't want to save in your config state.

The content of the files that you list in `[preset].yaml` will be mirrored to `.config/config-woman/[preset]_files/`.
Owner, group and mode will be saved and later applied properly.

Just re-run the command to see what is left to do to come to a clean state.

Later on when you remove packages and files from your system and run the save command again you might have packages,
files and exclude rules listed in the `[preset]_redundant.yaml` file.  
That means those are listed in your config, but you don't have them installed/on the system/used to exclude files.
Either you apply the config state to make your system compliant to the config state or remove those from
the `[preset].yaml` file to make your config state compliant to the system state.

#### Apply system config to system state

```
python3 main.py system apply [preset]
```

This is basically the reverse of saving. Same rules apply.

### User mode

#### Save user state to config

The default preset for system mode is named `default_user`:

```
python3 main.py user save [preset]
```

This basically does the same as system saving, but without packages, and it only looks at files in `.config`, and files
in `~/` that start with a `.`.  
All the same rules apply, except that path are relative to `~/`.

#### Apply user config to user state

```
python3 main.py user apply [preset]
```

This is basically the reverse of saving. Same rules apply.

### Note

If you put your config into a VCS-controlled repository (which you really should do), you should
ignore `[preset]_missing.yaml` and `[preset]_redundant.yaml`.

## Development

You can use the `--config-directory/-c` option to control where files get saved. I find it easiest to just use `-c .` (
the files that will be created are ignored by the .gitignore).

Test live in the `tests/` directory. Every test should be named
like `test_[mode]_[action]_[what is tested]_[systems].py` where:

- `mode` can be either `system` or `user`
- `action` can be either `save` or `apply`
- `systems` can be:
    - `all` (for system independent tests)
    - `pacman` (for systems with pacman package manager)
    - `apt` (for systems with apt package manager)
    - `arch` (for Arch Linux)
    - `manjaro` (for Manjaro)
    - `debian` (for Debian)
    - `ubuntu` (for Ubuntu)

To run all tests with docker run `./run-tests.sh`.  
On the first run it will take a while until the tests start, because the images are being built.  
You can also pass the paths of the tests to the script like
this: `./run-tests.sh tests/test_info_pacman.py tests/test_info_apt.py`.  
Executing these tests is not super-fast, but proper isolation and controlled state for each test is needed.