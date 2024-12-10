from website import create_app


app = create_app()

if __name__ == "__main__": #run the web server if we directly run this file  
  app.run( debug=True)
  
