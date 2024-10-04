 @cups.md  using the cups docs -- help me set up the printer so that it prints the labels I have.

they are 2 x 4 inches and they enter the printer from the short-edge but I want them to be printed on the labels landscape: meaning that the words are oriented so that if you are reading it correctly the long-edges are on the top and the bottom.

I am building a system to check people into events and automatically print a name tag for them with their info. The user will scan a qr code that opens a web app that will prompt them for their phone number. if they are recognized, they'll get a OTP code texted to them and well save their check in to the event. Then it'll ping the raspberry pi 'host name: hello-miami-pi) that is connected to the label marker printer.

if they are a new user, they'll be prompted to sign-up with their first, last name, email, twitter or just sign-up with google. Then it'll save their event check-in and print out their name tag. So I'll need to set up the printer to print the labels in landscape mode and with a template that I can modify to add the info I need.

@hello-miami-pi is a SFTP-sync'ed dir that is synced with the rasbery-pi


------------
# Label Maker Setup and Integration

## Printer Setup

1. Connect the label printer to the Raspberry Pi (hello-miami-pi) via USB.

2. Install CUPS and necessary dependencies:
   ```bash
   sudo apt-get update
   sudo apt-get install cups cups-client python3-cups
   ```

3. Add your user to the lpadmin group and restart CUPS:
   ```bash
   sudo usermod -aG lpadmin $USER
   sudo systemctl restart cups
   ```

4. Enable the CUPS web interface:
   ```bash
   sudo cupsctl --remote-any
   sudo systemctl restart cups
   ```

5. Access the CUPS web interface at `http://<raspberry-pi-ip>:631`.

6. Add the label printer:
   - Navigate to "Administration" > "Add Printer"
   - Select your USB-connected label printer
   - Set the following options:
     - Name: `hello_miami_label_printer` (use this name in the print service)
     - Media size: Custom.2x4in
     - Orientation: Landscape
     - Print quality: Adjust based on printer capabilities (e.g., 300dpi)

7. Configure the printer for 2x4 inch labels in landscape mode:
   ```bash
   lpoptions -p hello_miami_label_printer -o media=Custom.2x4in -o orientation-requested=4
   ```

## Label Template Setup

1. Create an HTML template for name tags:
   ```html
   <!DOCTYPE html>
   <html>
   <head>
     <meta charset="UTF-8">
     <style>
       @page {
         size: 4in 2in landscape;
         margin: 0;
       }
       body {
         width: 4in;
         height: 2in;
         display: flex;
         flex-direction: column;
         justify-content: center;
         align-items: center;
         font-family: Arial, sans-serif;
       }
       .name {
         font-size: 24pt;
         font-weight: bold;
       }
       .info {
         font-size: 12pt;
       }
     </style>
   </head>
   <body>
     <div class="name">{{ name }}</div>
     <div class="info">{{ info }}</div>
   </body>
   </html>
   ```

2. Save this template as `/home/pi/hello-miami-pi/templates/nametag_template.html`.

## Printing Service Setup

1. Install required Python packages:
   ```bash
   pip install fastapi uvicorn jinja2 weasyprint pycups
   ```

2. Create `/home/pi/hello-miami-pi/print_service.py`:
   ```python
   from fastapi import FastAPI, HTTPException
   from pydantic import BaseModel
   from jinja2 import Environment, FileSystemLoader
   from weasyprint import HTML
   import cups
   import tempfile
   import os

   app = FastAPI()
   env = Environment(loader=FileSystemLoader('/home/pi/hello-miami-pi/templates'))
   conn = cups.Connection()

   class NameTag(BaseModel):
       name: str
       info: str

   @app.post("/print_nametag")
   async def print_nametag(nametag: NameTag):
       template = env.get_template('nametag_template.html')
       html_content = template.render(name=nametag.name, info=nametag.info)

       with tempfile.NamedTemporaryFile(suffix='.pdf', delete=False) as tmp:
           HTML(string=html_content).write_pdf(tmp.name)

       try:
           job_id = conn.printFile('hello_miami_label_printer', tmp.name, "Nametag", {})
           os.unlink(tmp.name)
           return {"status": "success", "message": f"Nametag printed successfully, job ID: {job_id}"}
       except cups.IPPError as e:
           os.unlink(tmp.name)
           raise HTTPException(status_code=500, detail=f"Printing failed: {str(e)}")

   if __name__ == "__main__":
       import uvicorn
       uvicorn.run(app, host="0.0.0.0", port=8000)
   ```

3. Set up the print service to start on boot:
   ```bash
   sudo nano /etc/systemd/system/print_service.service
   ```
   Add the following content:
   ```ini
   [Unit]
   Description=Hello Miami Print Service
   After=network.target

   [Service]
   User=pi
   WorkingDirectory=/home/pi/hello-miami-pi
   ExecStart=/usr/bin/python3 /home/pi/hello-miami-pi/print_service.py
   Restart=always

   [Install]
   WantedBy=multi-user.target
   ```
   Enable and start the service:
   ```bash
   sudo systemctl enable print_service
   sudo systemctl start print_service
   ```

## Integration with Main Application

1. Update the main FastAPI application (`main.py`) to include the check-in endpoint:
   ```python
   import httpx
   from fastapi import APIRouter, BackgroundTasks, HTTPException
   from pydantic import BaseModel

   router = APIRouter()

   class CheckInData(BaseModel):
       first_name: str
       last_name: str
       email: str

   async def print_nametag(data: CheckInData):
       async with httpx.AsyncClient() as client:
           try:
               response = await client.post(
                   "http://hello-miami-pi:8000/print_nametag",
                   json={"name": f"{data.first_name} {data.last_name}", "info": data.email},
                   timeout=10.0
               )
               response.raise_for_status()
           except httpx.HTTPStatusError as e:
               print(f"Printing failed: {e}")
           except httpx.RequestError as e:
               print(f"Network error: {e}")

   @router.post("/checkin")
   async def checkin(data: CheckInData, background_tasks: BackgroundTasks):
       # Process check-in logic here

       # Trigger nametag printing in the background
       background_tasks.add_task(print_nametag, data)

       return {"status": "success", "message": "Check-in complete, nametag printing initiated"}
   ```

2. Ensure proper network configuration:
   - Set a static IP for the Raspberry Pi or use mDNS (e.g., `hello-miami-pi.local`)
   - Update the main application's DNS or hosts file to resolve `hello-miami-pi`

## Infrastructure Considerations

1. Network Security:
   - Implement authentication for the print service API (e.g., API key, JWT)
   - Use HTTPS for all communications (set up SSL certificates)
   - Configure firewall rules to restrict access to the print service

2. Error Handling and Monitoring:
   - Implement logging in both the main application and print service
   - Set up monitoring for the print service (e.g., Prometheus, Grafana)
   - Create alerts for printer errors or low supplies

3. Scaling:
   - For multiple printers, implement a print job queue system (e.g., Redis-based queue)
   - Consider load balancing if using multiple Raspberry Pis for printing

## Web App Enhancements

1. User Interface:
   - Add a loading indicator during check-in
   - Provide real-time feedback on nametag printing status

2. Error Handling:
   - Implement retry logic for failed print jobs
   - Allow manual triggering of nametag printing from the admin interface

3. Admin Interface:
   - Create a dashboard for monitoring printer status and job queue
   - Implement functionality for reprinting nametags and managing printer settings

## Deployment and Testing

1. Set up a staging environment that mirrors the production setup
2. Implement end-to-end tests covering the entire check-in and printing flow
3. Perform load testing to ensure the system can handle expected concurrent users
4. Develop a rollback plan in case of critical issues during deployment
5. Create documentation for troubleshooting common printer and network issues

This enhanced setup provides a more robust and scalable solution for integrating the label maker into the Hello Miami Messaging App. It includes detailed instructions for setting up CUPS, configuring the printer, and creating a reliable print service. The integration with the main application is designed to handle printing asynchronously, improving the user experience during check-in.
