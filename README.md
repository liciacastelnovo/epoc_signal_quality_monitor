# Emotiv EPOC 1.0 — Signal Quality Monitor

A small Python script to monitor, in real time, the contact quality of the
14 EEG sensors on an **Emotiv EPOC 1.0** headset, using the
[emokit](https://github.com/openyou/emokit) library.

*This project is not affiliated with, endorsed by, or supported by Emotiv
Inc. "Emotiv" and "EPOC" are trademarks of their respective owner, used
here only to describe hardware compatibility.*

## Hardware

This project was built and tested specifically for the **Emotiv EPOC 1.0**
(the original 2010-era model, not the EPOC+ or later versions). It relies on
the headset's proprietary 2.4GHz USB dongle.

Because this hardware is old, the wireless link between the headset and the
dongle can be sensitive to radio interference on the 2.4GHz band. In
particular, **a nearby smartphone can disrupt the connection** and cause the
script to lose the signal and repeatedly attempt to reconnect. If you
experience connection drops, try moving other 2.4GHz devices (phones, other
wireless peripherals) away from the dongle.

## Why this project exists

Emotiv's own current software (EmotivPRO) still officially lists the
classic EPOC as supported, and is available as a paid subscription. Among
open-source alternatives, I wasn't able to find one that's actively
maintained today — projects like
[python-emotiv](https://github.com/ozancaglayan/python-emotiv) (which its
own repository describes as Linux-only, using `pyusb`/`udev` rather than
`hidapi`, so it isn't directly usable on macOS as-is) and
openepoc, built around the same reverse-engineered protocol as `emokit`,
were all abandoned years ago (the python-emotiv author
[explicitly says so](https://github.com/ozancaglayan/python-emotiv) in the
README). `emokit` itself hasn't been touched since it was archived, hence
the fork and patches in this repository.

## Setup

The library dependencies for this project (`emokit`, `pyhidapi`,
`pycryptodome`) are old and, in some cases, incompatible with modern Python
versions and the current PyPI release of `emokit`. This project installs
`emokit` from a maintained fork instead of PyPI, with a couple of
compatibility fixes applied:

```bash
brew install python@3.11 hidapi
python3.11 -m venv .venv311
source .venv311/bin/activate
pip install pyhidapi pycryptodome
pip install git+https://github.com/liciacastelnovo/emokit.git#subdirectory=python
```

Python 3.11 is used instead of a newer version because some of these
libraries fail to install or run correctly on newer Python releases.

## Usage

```bash
source .venv311/bin/activate
python main.py
```

Press `Ctrl+C` to stop.

**Note:** running the script directly from a terminal gives a cleaner,
better-formatted display than running it from an IDE's built-in console
(e.g. PyCharm's Run window). This is because the script clears the screen
between updates using a terminal command that isn't fully supported in
some IDE consoles, so the output there may stack up instead of refreshing
in place. The script works correctly either way — only the on-screen
display differs.

## Reading the output

Each row of the table corresponds to one sensor. Here's how to read each
column:

- **Channel**: one of the 14 EEG sensor positions, named according to the
  International 10-20 system (e.g. `AF3`, `F7`, `O1`...). The letters
  indicate the scalp region (`F` = Frontal, `AF` = Anterior Frontal,
  `FC` = Fronto-Central, `T` = Temporal, `P` = Parietal, `O` = Occipital);
  odd numbers are on the left hemisphere, even numbers on the right.
- **Value**: the raw EEG signal reading for that channel at that instant.
  This number constantly fluctuates (positive and negative) because it
  reflects real brain activity — there's no "correct" value to aim for.
  It's mainly useful as a sanity check: what matters is that it keeps
  changing. A value stuck at 0 or at a fixed number usually means the
  sensor isn't picking up any signal at all.
- **Quality**: contact quality between the sensor and the scalp. This value
  is extracted from a 14-bit field in the raw sensor packet. According to
  `emokit`'s own protocol documentation
  ([emotiv_protocol.asciidoc](https://github.com/openyou/emokit/blob/master/doc/emotiv_protocol.asciidoc)),
  it represents "the amplitude of [the sensor's] calibration signal," with
  a theoretical range of **0–16383** (14 bits) — **higher is better**. That
  same documentation recommends dividing the raw reading by ~540 to get a
  more interpretable number, where **0.8–1.0 indicates good contact**.

### About the two reference electrodes

The EPOC has 16 physical sensors in total, but only 14 appear as EEG
channels with a quality value in the data this project reads. The
remaining two — **CMS** (at position P3) and **DRL** (at position P4) —
serve as Emotiv's shared electrical reference points for all other
channels. `emokit` doesn't expose any data for these two positions
(confirmed by inspecting the raw packet during testing), so this project
has no visibility into their individual contact quality. Emotiv's own
documentation describes a single contact-quality system used across their
headset range, with P3/P4 listed as named channel positions in the classic
EPOC's specifications, so it's possible the original Control Panel
software displayed a quality indicator for these two as well — but that's
outside what this project can confirm.

In practice: if you've positioned all 14 EEG sensors well but many of them
still show poor quality at the same time, this is usually a sign that the
CMS/DRL reference electrodes are poorly positioned, rather than a problem
with the individual sensors themselves.

### Battery and gyroscope

Below the sensor table, the script also shows:

- **Battery**: the headset's battery percentage. This is only included in
  one out of every 128 packets (roughly once per second), so the script
  keeps showing the last known value between updates rather than leaving
  it blank most of the time.
- **Gyro(x) / Gyro(y)**: raw readings from the headset's built-in 2-axis
  gyroscope, which tracks head movement (turning left/right and
  forward/back). These aren't used for contact quality, but are read from
  the same data packets and shown for reference.

## License

The `emokit` library is public domain. This project's own code is provided
as-is for personal research use.
