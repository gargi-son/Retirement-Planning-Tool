Use the /testSystemInput path for testing system inputs with the api first
Server cannot handle running optimizer more than once in a request. so must make multiple fetch calls on the front end
To start server/see results: 
- cd to flask-server-code-to-deploy 
- execute command: flask run
- in browser go to: 
  http://127.0.0.1:5000/getrecs : to see system output given input example in system_input_ex.json
  http://127.0.0.1:5000/testSystemInput : to see how your inputs are sent to server 
  http://127.0.0.1:5000/ : to see how just optimizer  runs on combined_accounts_model_input_var.json
  
  
  
