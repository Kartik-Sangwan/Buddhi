from main import app, db
import os
if __name__ == '__main__':
	port = int(os.environ.get('PORT', 5000))
	app.run(host = '0.0.0.0', port=port)
	# db.create_all()
