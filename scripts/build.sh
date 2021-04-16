SCRIPTDIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
PROJDIR="${SCRIPTDIR}/../toolkit/"


function exec_black_check () {
  black --check "${PROJDIR}"  || exit 1
}

function exec_sonar () {
    sonar-scanner -Dsonar.projectVersion=$(cat "${PROJDIR}/VERSION") -Dproject.settings=./.scripts/sonar-project.properties || exit 1
}

function exec_tests () {
    test_files=$(find "${SCRIPTDIR}/../tests" -name test\*.py)

    if [[ -z ${test_files} ]]; then
        echo "no unit tests to execute"
    else
        export PYTHONPATH=${PROJDIR}../ &&  pytest --cov-report=xml --cov="${PROJDIR}" tests || exit 1
    fi
}

function exec_check () {
    exec_black_check
    exec_tests
    #exec_sonar

    exit 0
}


COMMAND="$1"
case ${COMMAND} in
  -c|--check)
    exec_check
    shift
    ;;
  *)
    ERROR "Unknown argument: ${COMMAND}" 
    ;;
esac