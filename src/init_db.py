from database import Database

def init_db():
    db = Database({
        "host": "localhost",
        "user": "harmabel",
        "password": "Tocan5253!",
        "database": "campersystem"
    })

    db.connect()
    return db