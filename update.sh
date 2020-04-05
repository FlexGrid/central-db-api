#!/bin/bash
set -euxo pipefail

error_handler() {
  echo "******* FAILED *******" 1>&2
}

trap error_handler ERR

# enter deploy directory
cd "$(dirname "${BASH_SOURCE[0]}")"

eval $(ssh-agent)
ssh-add ~/.ssh/id_rsa

git pull
sudo systemctl restart eveoauth2.service
