from models import db, Story, Paragraph
from flask import Flask,request, jsonify, make_response, send_from_directory
from flask_cors import CORS
import os
from flask_restful import Resource,Api
from werkzeug.utils import secure_filename
from flask_migrate import Migrate
from flask_restful import Resource, Api
from datetime import datetime
import json


app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URI')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.json.compact = False

CORS(app)
api = Api(app)

db.init_app(app)

migrate =  Migrate(app, db)


# Configure secret keys
app.secret_key = os.getenv('FLASK_SECRET_KEY', 'default_secret_key')
app.config['JWT_SECRET_KEY'] = os.getenv('JWT_SECRET_KEY', 'default_jwt_secret_key')

UPLOAD_FOLDER = 'Images'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER


if not os.path.exists(app.config['UPLOAD_FOLDER']):
    os.makedirs(app.config['UPLOAD_FOLDER'])


class StoryResource(Resource):
    def get(self):
        stories = Story.query.all()
        return [story.to_dict() for story in stories], 200
    
    def post (self):
        
        data = request.form
        file = request.files.get('photo')

        filename = secure_filename(file.filename)
        file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))

        if not data:
            return jsonify({'error': 'No data available for posting'}), 400
        
        required_fields = ['title','author','category','date']
        for field in required_fields:
            if field not in data:
                return jsonify({'error': f'Missing required field: {field}'}), 400
            
            title = data.get('title')
            author = data.get('author')

            # Convert date string to Python date object
            date_str = data.get('date')
            date = datetime.strptime(date_str, '%Y-%m-%d').date()

            category = data.get('category')

            new_story = Story (
                title=title,
                author=author,
                date=date,
                category=category
            )

            paragraphs = json.loads(data.get('paragraphs', "[]"))

            for paragraph in paragraphs:
                if 'paragraph' not in paragraph:
                    return jsonify({'error': 'Missing required field: paragraph'}), 400
            
            new_paragraph = Paragraph(paragraph=paragraph['paragraph'])
            new_story.paragraphs.append(new_paragraph)

            try:
                db.session.add(new_story)
                db.session.commit()
                return jsonify(new_story.to_dict()), 200
            except Exception as e:
                db.session.rollback()
                return jsonify({'error': f'Failed to create story: {str(e)}'}), 500
            
api.add_resource(StoryResource, '/stories')

@app.route('/images/<filename>')
def upload_images(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename), 200

@app.route('/story/<int:id>', methods=['GET', 'DELETE', 'PATCH'])
def get_story_by_id(id):
    story = Story.query.filter_by(id=id).first()

    if not story:
        return jsonify({'error': 'Story does not exist'}), 404

    if request.method == 'GET':
        return jsonify(story.to_dict()), 200
    
    if request.method == 'PATCH':

        data = request.form.to_dict()

        file = request.files.get('photo')
        filename = secure_filename(file.filename)
        file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))

        if 'photo' in data:
            try:
                data['photo'] = filename
            except ValueError:
                return jsonify({'error': 'Invalid Image File'}), 400
        
        if 'date' in data:
            try:
                data['date'] = datetime.strptime(data['date'], '%Y-%m-%d').date()
            except ValueError:
                return jsonify({'error': 'Invalid date format. Date must be in YYYY-MM-DD format'}), 400
        
        paragraphs = json.loads(data.get('paragraphs', '[]'))

        if not paragraphs:
            return jsonify({"error":"No description has been provided"}), 400
        
        story.paragraphs.clear()

        for paragraph in paragraphs:
            if 'paragraph' not in paragraph:
                return jsonify({'error': 'Missing required field: paragraph'}), 400
            
        new_paragraph = Paragraph(paragraph=paragraph['paragraph'])
        story.paragraphs.append(new_paragraph)

        for key, value in data.items():
            setattr(story,key,value)

        try:
            db.session.commit()
            return jsonify(story.to_dict()), 200
        except Exception as e:
            db.session.rollback()
            return jsonify({'error': f'Failed to update story: {str(e)}'}), 500 
        
    if request.method == 'DELETE':

        try:
            db.session.delete(story)
            db.session.commit()
            return jsonify({'message': 'Invoice deleted successfully'}), 200
        except Exception as e:
            db.session.rollback()
            return jsonify({'error': f'Failed to delete Story: {str(e)}'}), 500
                

if __name__ == '__main__':
    app.run(port=1904, debug=True)
