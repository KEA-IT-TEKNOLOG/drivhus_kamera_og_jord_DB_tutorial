from flask import Flask, render_template, redirect, url_for
import libcamera
from picamera2 import Picamera2
from datetime import datetime
from sqlite3 import Connection

def select_images(amount):
    if isinstance(amount, int) and amount > 0:
        con = Connection('greenhouse.db')
        cur = con.cursor()
        sql = f"""SELECT timestamp FROM Images ORDER BY rowid DESC LIMIT {amount}"""
        cur.execute(sql)
        img_rows = cur.fetchall()
        print(img_rows)
        con.close()
        return img_rows

def insert_img(timestamp):
    con = Connection('greenhouse.db')
    cur = con.cursor()
    params = (timestamp,)
    sql = """INSERT INTO Images (timestamp) VALUES(?)"""  
    cur.execute(sql, params)
    con.commit()
    con.close()

def take_picture():
    date_time = datetime.now()
    datetime_img = f"{date_time.strftime('%d-%m-%Y-%H:%M:%S')}.jpg"
    picam = Picamera2()
    config = picam.create_preview_configuration(main={"size": (640, 480)})
    config["transform"] = libcamera.Transform(hflip=1, vflip=1)
    picam.configure(config)    
    picam.start()
    picam.capture_file(f"static/img/{datetime_img}")
    picam.close()
    insert_img(datetime_img)

app = Flask(__name__)

@app.route("/take_photo/")
def take_photo():
    # tager et nyt billede
    take_picture()
    # laver et redirect tilbage til home når billedet er taget
    return redirect(url_for("home"))

@app.route("/")
def home():
    # tager den returnerede liste med tuples fra cur.fetchall()
    # for at få det seneste billede tages de første tuple i listen
    # derefter tages den første item i tuplen 
    return render_template("home.html", image = select_images(1)[0][0])

@app.route("/gallery/")
def gallery():
    image_rows = select_images(10)
    return render_template("gallery.html", image_rows = image_rows)

@app.route("/site2/")
def site2():
    return render_template("site2.html")

if __name__ == ('__main__'):
    app.run(host="0.0.0.0", debug=True)
