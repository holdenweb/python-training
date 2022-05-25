test:
	(date; poetry run pytest -v tests)

pull:
	(date; poetry run python src/transformers/load_data.py 1yFZLLz2Juln2s5nz26HcEPXOMMNbubeyPophqOIStFI data!A7:C272) | tee -a pull.log
dump:
	date=$$(date "+%Y%m%dT%H%M%S") && mongodump -d WebDB -c team_member --archive=dumps/team_member.$$date
reports:
	poetry run python src/team_history.py
backup:
	mongodump --db WebDB --out=dumps/$$(date +%y-%m-%dT%H:%M:%S)
