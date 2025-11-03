#!/bin/bash
cd /home/rhy/OpenCode
. voice_env/bin/activate
pip uninstall torch -y
pip install torch --index-url https://download.pytorch.org/whl/cu124