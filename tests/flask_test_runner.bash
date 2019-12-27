# FLASK_ENV=dev_testing LOGS=off python -m unittest -v test_app${1}${2}

function testRunner(){
    # run all or if $1 is empty
    if [ "${1}" == "all" ] ||  [ -z "${1}" ]
    then
        echo "ONE"
        FLASK_ENV=dev_testing LOGS=off python -m unittest discover -p "test_*.py"
        # run specific files by file name
    elif [ "${1}" != "all" ] && [ ! -z "${1}" ]
    then
        echo "TWO"
        if [ -z "${1}" ]; then
            echo "blank"
        else
            echo "not"
        fi
        echo FLASK_ENV=dev_testing LOGS=off python -m unittest discover -p $1
        FLASK_ENV=dev_testing LOGS=off python -m unittest discover -p $1
        # run all - default
    else
        echo "THREE"
        FLASK_ENV=dev_testing LOGS=off python -m unittest discover -s tests  -p "test_*.py"
    fi
}
testRunner $1
tests/utilities/test_driver_scraper.py