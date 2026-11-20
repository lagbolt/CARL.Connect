py check-language.py -i new-records.mrc -o check-language-report.txt -b
py check-names.py -i new-records.mrc -o check-names-report.txt
py check-records.py -i new-records.mrc -o check-records-report.txt -b
py check-subjects.py -i new-records.mrc -o check-subjects-report.txt
echo Starting series check ...
py check-series.py -i new-records.mrc -o check-series-report.csv
echo Done!