# Installation (macOS)


Install relevant packages from homebrew.

```bash
brew install portaudio
brew install libusb
brew install blackhole-2ch
```

Create a conda environment and install the requiste packages from pip.

```bash
conda create -n lighting python=3.11
conda activate lighting
pip install -r requirements.txt
```

Set the following env variable.

```bash
export BLINKA_FT232H=1
```


Finally, start the process

```bash
python main.py
```
