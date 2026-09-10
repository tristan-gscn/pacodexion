# pacodexion

A high-precision automated tester and concurrency validator for the **42 Codexion** project.

## Installation

```bash
pip install pacodexion
```

## Usage

Once installed, the `pacodexion` command is available in your shell.

### Run all tests

By default, `pacodexion` tests `./codexion`:

```bash
pacodexion
```

You can specify a custom binary path using `-b` or `--binary`:

```bash
pacodexion -b path/to/codexion
```

### Run specific test cases

You can pass one or more test keys or names:

```bash
# Run tests 1, 2, and starvation
pacodexion 1 2 starvation

# Run with a custom binary path
pacodexion -b ../codexion/coders/codexion tight_timings
```

### List all test cases

To see all available test cases, their exact CLI arguments, and what each test evaluates:

```bash
pacodexion --list
# or
pacodexion -l
```

## Test Results

`pacodexion` evaluates each test case with one of three statuses:

- **`[OK]`**: The simulation passed all specifications and timing constraints.
- **`[WARN]`**: The simulation succeeded, but a minor OS scheduling deviation was detected (e.g. slight timer jitter or burnout delay within acceptable OS tolerance). Exit code is `0`. A trace is saved in `traces/warn/` highlighting the deviation.
- **`[KO]`**: A strict violation occurred (concurrency race, adjacent coders compiling simultaneously, dongle cooldown violation, delayed burnout beyond tolerance, actions logged after burnout, or unhandled invalid arguments). Exit code is `1`. A detailed trace is saved in `traces/ko/` with `PROBLEM HERE >>>` highlighting the faulty line.
