import web
import ardustat_library_no_class as ard
import socket

urls = (
	'/','generic'	
)


app = web.application(urls, globals())

class generic:
	def GET(self):
		web.header('Content-Type','text/html; charset=utf-8', unique=True)	
		try:
			ard.connect(7777)
		except:
			foo = "whoops"
		ard.blink()
		return ard.parsedread()
		

if __name__ == "__main__": app.run()
