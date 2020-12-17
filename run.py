from flask_blog import app

if __name__ == '__main__' :                             # Using this, we dont need to set env variable every time, just use python (.py filename) in same dir
    app.run(debug=True)