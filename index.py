from flask import Flask, render_template

app=Flask(__name__)


@app.route('/')
def principal():
    return render_template("index.html")


@app.route('/Servicios')
def servicios():
    return render_template("servicios.html")


@app.route('/Contactos')
def contacto():
    return render_template("contacto.html")

if __name__ == '__main__':
    app.run(debug=True, port=5020)
