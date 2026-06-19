# Intended Architecture

Workers should call `service.py`. Only the service layer should import `db.py`.
