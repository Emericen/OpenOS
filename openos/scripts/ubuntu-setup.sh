#!/bin/bash
set -e  # Exit immediately if any command fails

echo "🔧 Updating and installing core packages..."
sudo apt update && sudo apt upgrade -y
sudo apt install -y git software-properties-common curl

echo "🐍 Installing Python 3.10 and tools..."
sudo add-apt-repository ppa:deadsnakes/ppa -y
sudo apt update
sudo apt install -y python3.10 python3.10-venv python3.10-distutils

echo "📦 Installing pip for Python 3.10..."
curl -sS https://bootstrap.pypa.io/get-pip.py | sudo python3.10

echo "🔗 Setting 'python' to point to python3.10..."
sudo update-alternatives --install /usr/bin/python python /usr/bin/python3.10 1
sudo update-alternatives --set python /usr/bin/python3.10
echo "✅ Python version set to: $(python --version)"

echo "🔗 Setting 'pip' to point to pip3.10..."
sudo update-alternatives --install /usr/bin/pip pip /usr/local/bin/pip3.10 1
sudo update-alternatives --set pip /usr/local/bin/pip3.10
echo "✅ Pip version set to: $(pip --version)"

echo "📁 Cloning openos repo..."
cd /home/user
git clone https://github.com/Emericen/openos.git

echo "📂 Installing openos package..."
cd /home/user/openos
sudo apt-get install -y linux-libc-dev libevdev-dev
sudo apt install -y build-essential python3.10-dev
python3.10 -m pip install mss==10.0.0
python3.10 -m pip install pynput==1.7.8
python3.10 -m pip install numpy==2.2.3

echo "🎉 Setup complete! You can now run OpenOS."
