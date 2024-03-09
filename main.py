from website import create_app

app = create_app()
print(__name__)
if __name__ == '__main__' or __name__ == 'main':
    app.run(debug=True)
    
    