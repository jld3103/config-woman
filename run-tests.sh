#!/bin/bash
source venv/bin/activate
set -e
pip freeze | grep -v "config-woman" >requirements.txt
docker build . -t config-woman-source -q

arch_image="archlinux:latest"
manjaro_image="manjarolinux/base:latest"
debian_image="debian:latest"
ubuntu_image="ubuntu:latest"

for image in $arch_image $manjaro_image $debian_image $ubuntu_image; do
  docker pull $image -q &
done
wait

pacman_base="RUN pacman -Sy python --noconfirm"
apt_base="RUN apt-get update && apt-get install python3 python3-venv -y
RUN ln -sf \$(which python3) /usr/bin/python"

if [ $# -eq 0 ]; then
  files=(tests/*/test_*.py)
else
  files=("$@")
fi

for file in "${files[@]}"; do
  name="$(basename "$file")"
  dir="$(dirname "$file")"
  os="$(echo "$name" | cut -d "_" -f 2)"
  base=""
  if [[ "$os" == "arch" ]]; then
    base="FROM $arch_image
$pacman_base"
  elif [[ "$os" == "manjaro" ]]; then
    base="FROM $manjaro_image
$pacman_base"
  elif [[ "$os" == "debian" ]]; then
    base="FROM $debian_image
$apt_base"
  elif [[ "$os" == "ubuntu" ]]; then
    base="FROM $ubuntu_image
$apt_base"
  fi
  cat >"$dir/Dockerfile" <<EOF
$base
WORKDIR /app
ENV VIRTUAL_ENV="/app/venv"
ENV PATH="\$VIRTUAL_ENV/bin:\$PATH"
ENV CONFIG_DIR="/app"
RUN python -m venv ./venv
COPY --from=config-woman-source /app /app
RUN pip install -r requirements.txt
COPY $name $name
CMD ["pytest", "$name"]
EOF
  docker build "$dir" -t "$name" -q
  rm -rf "$dir/Dockerfile"
  docker run --rm "$name"
done
