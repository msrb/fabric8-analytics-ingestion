#!/bin/bash -ex
chmod +x runtests.sh

export PYTHONPATH=`pwd`/f8a_ingestion
echo "Create Virtualenv for Python deps ..."
function prepare_venv() {
    VIRTUALENV=`which virtualenv`
    if [ $? -eq 1 ]; then
        # python34 which is in CentOS does not have virtualenv binary
        VIRTUALENV=`which virtualenv-3`
    fi

    ${VIRTUALENV} -p python3 venv && source venv/bin/activate
    pip install -U pip
    python3 `which pip3` install -r requirements.txt
    python3 `which pip3` install radon

}

[ "$NOVENV" == "1" ] || prepare_venv || exit 1

`which pip3` install pytest
`which pip3` install pytest-cov

echo "*****************************************"
echo "*** Cyclomatic complexity measurement ***"
echo "*****************************************"
radon cc -s -a -i venv .

echo "*****************************************"
echo "*** Maintainability Index measurement ***"
echo "*****************************************"
radon mi -s -i venv .

echo "*****************************************"
echo "*** Unit tests ***"
echo "*****************************************"
PYTHONDONTWRITEBYTECODE=1 python3 `which pytest` --cov=f8a_ingestion/ --cov-report term-missing -vv tests/
