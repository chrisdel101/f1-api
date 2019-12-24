# FLASK_ENV=dev_testing LOGS=off python -m unittest -v test_app${1}${2}

function testRunner(){
    # run all
    if [ "${1}" == "all" ]
    then
        echo "ONE"
        FLASK_ENV=dev_testing LOGS=off python -m unittest discover -s tests  -p "test_*.py"
        # run specific files by file name
    elif [ "${1}" != "all" ] && [ "${1}" != [[:space:]] ]
    then
        echo "TWO"
        FLASK_ENV=dev_testing LOGS=off python -m unittest discover -s tests -p $1
        # run all - default
    else
        echo "THREE"
        FLASK_ENV=dev_testing LOGS=off python -m unittest discover -s tests  -p "test_*.py"
    fi
}
testRunner $1