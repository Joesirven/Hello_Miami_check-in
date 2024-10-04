 @cups.md  using the cups docs -- help me set up the printer so that it prints the labels I have.

they are 2 x 4 inches and they enter the printer from the short-edge but I want them to be printed on the labels landscape: meaning that the words are oriented so that if you are reading it correctly the long-edges are on the top and the bottom.

I am building a system to check people into events and automatically print a name tag for them with their info. The user will scan a qr code that opens a web app that will prompt them for their phone number. if they are recognized, they'll get a OTP code texted to them and well save their check in to the event. Then it'll ping the raspberry pi 'host name: hello-miami-pi) that is connected to the label marker printer.

if they are a new user, they'll be prompted to sign-up with their first, last name, email, twitter or just sign-up with google. Then it'll save their event check-in and print out their name tag.

@hello-miami-pi is a SFTP-sync'ed dir that is synced with the rasbery-pi

@app is the parent dir for the whole app.

@hello_miami_messaging_app is the web-app that I want to use. It will server as a CRM, sms and email blasting service, and 1:1 convo service. I want to incporporate the event check-in & account-management service I mentioned above with the app. The event check-ins will be saved

Notes:
- fast api & supbase for backend - pydantic to handle data typing and schemas
- twilio for sms service
- i forgot the name of the emialling service
- Solid.js Frontend in the client dir in @hello_miami_messaging_app  (I need extra guidance here -- I've never used it and I want your help to learn so be verbose when explaining this and how it works under the hood)
- testing the api is important too
-

Instructions:
- Review the folders and fiels I've refrenced and understand their current state.
-I want you to produce a specs md doc for the whole project with suggested prompts and development process.
guide me in inplementing those instrucutions
