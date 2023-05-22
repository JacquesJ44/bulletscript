# This file will read the selected tsv file and import the data into the STOCK table of email.db
# The fields to be used are id, description, value and count

from app import app

from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy(app)

with app.app_context():
    #Creating a class stock - table STOCK of the db
    class Stock(db.Model):
        __tablename__ = 'stock'
        id = db.Column(db.Integer, primary_key=True)
        description = db.Column(db.String(50))
        count = db.Column(db.Integer)

    # clear out the current data in the table - if any
    db.session.query(Stock).delete()
    db.session.commit()

    # update the table with the new values
    items = []

    with open('BS Merch MASTER LIST.xlsx - Inventory Report.tsv') as file:
        for line in file:
            l=line.split('\t')
            items.append(l)

    for i in range(len(items)):
        description = items[i][1]
        count = items[i][8]
        
        add_record = Stock(description=description, count=count)
        db.session.add(add_record)
        db.session.commit()

    print('SUCCESS')