#!/bin/bash
set -euxo pipefail

error_handler() {
  echo "******* FAILED *******" 1>&2
}

ssh -t dss@db.flexgrid-project.eu flexgrid/eve-oauth2/update.sh
