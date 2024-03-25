# Deps check

Run a set of tests or checks to see if commands run successfully or files exist

## Usage

```
python -m deps_check -f <file>
```

Without the `-f` flag, the script will look for a file named `deps.txt` in the current directory.

## File format

The file format looks similar to a makefile but with a few differences.

```
# Comment

%all: files directories commands nonzero

# If files exist then pass
files:
    @/bin/bash
    @example.txt

# If directories exist then pass
directories:
    @/bin/
    @deps_check/

# If command returns 0 then pass
commands:
    $ ls -l /this/does/not/exist
    $ echo "This will not be printed"

# If exists or returns other than 0, fail
nonzero:
    !@/bin/
    !$ ls -l /bin/bash
```

The `%all` target is required and is the target that will be run when the script is executed.

Rules can be defined in any order and can be named anything. The script will run the rules in the order they are defined in the `%all` target.

### Check types

- `@` - Passes check if the file exists
- `!@` - Passes check if the file does not exist
- `$` - Passes check if the command returns 0
- `!$` - Passes check if the command does not return 0

### Examples

This deps file will pass if python3 is installed:

```
%all: check_file check_command

# Check if the python executable is available
check_file:
    @/usr/bin/python3

# Test if python runs correctly
check_command:
    $/usr/bin/python3 -V
```

This deps file will pass if the `example.txt` file exists and the `example` directory does not exist:

```
%all: check_file check_directory

# Check if the example.txt file exists
check_file:
    @example.txt

# Check if the example directory does not exist
check_directory:
    !@example/
```

## Licence

This project is licecned under the GNU General Public License v3.0 - see the [LICENSE](LICENSE) file for details
