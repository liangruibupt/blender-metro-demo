#!/usr/bin/env bash
# Paint run prelude: swap on NVMe (Qwen-Image-Edit CPU offload > 32 GB host RAM) + all apt deps once,
# so the two parallel env installs below never fight over the dpkg lock. Marker ~/PRELUDE_DONE.
set -uo pipefail
exec > >(tee -a "$HOME/prelude.log") 2>&1
echo "=== prelude start $(date -u) ==="
if ! swapon --show | grep -q swapfile; then
  sudo fallocate -l 96G /opt/dlami/nvme/swapfile && sudo chmod 600 /opt/dlami/nvme/swapfile \
    && sudo mkswap /opt/dlami/nvme/swapfile && sudo swapon /opt/dlami/nvme/swapfile
fi
free -g
sudo apt-get update -y -q
sudo apt-get install -y -q python3.10 python3.10-venv python3.10-dev python3-venv python3-pip git ninja-build libegl1 libgl1
touch "$HOME/PRELUDE_DONE"; echo "PRELUDE_DONE $(date -u)"
