sqlite3 new-titles.db ".tables"
sqlite3 new-titles.db ".schema new_titles"
sqlite3 new-titles.db "SELECT status, count(*) FROM new_titles GROUP BY status"