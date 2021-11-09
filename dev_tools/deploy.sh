#! /bin/bash

set -e

BOARD=${BOARD:-u0}
echo "Selected serial port: ${BOARD}"
BASE_DIR=$(dirname $0)/..

case $1 in
    *deps)
        echo "uploading microdot"
        mpremote ${BOARD} cp ${BASE_DIR}/dependencies/microdot/src/*.py :
        ;;
    *lib)
        echo "uploading provisioning lib"
        mpremote ${BOARD} cp ${BASE_DIR}/src/*.py :
        ;;
    *ui)
        echo "uploading ui"
        mpremote ${BOARD} cp ${BASE_DIR}/src/*.html :
        ;;
    *)
        echo "Usage: $0 [deps|lib|ui]"
        exit 1
        ;;
esac