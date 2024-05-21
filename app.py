

from website import create_app



app = create_app()

if __name__ == "__main__": #run the web server if we directly run this file
  
  app.run( debug=True)
  
  

'''
#if u want to run app in server
app.run(port=5000, host='0.0.0.0')
'''



