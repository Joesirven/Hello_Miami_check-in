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
