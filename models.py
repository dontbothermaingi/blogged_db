from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class Story(db.Model):
    __tablename__ = 'stories'

    id = db.Column(db.Integer, primary_key=True, nullable=False)
    title = db.Column(db.String)
    author = db.Column(db.String)
    date = db.Column(db.String)
    category = db.Column(db.String)
    photo = db.Column(db.String)

    paragraphs = db.relationship('Paragraph', backref='story', cascade="all, delete-orphan", lazy=True)


    def to_dict(self):
        return{
            "id": self.id,
            "title": self.title,
            "author": self.author,
            "date": self.date,
            "category": self.category,
            "photo": f"/images/{self.photo}",
            "paragraphs":[paragraph.to_dict() for paragraph in self.paragraphs],
        }
    
    def __repr__(self):
        return (f"<Story id={self.id}, author={self.author}, subtitle={self.subtitle}, title={self.title}, date={self.date}"
                f"category={self.category}>")
    

class Paragraph(db.Model):
    __tablename__ = 'paragraphs'

    id = db.Column(db.Integer, primary_key=True, nullable=False)
    paragraph = db.Column(db.String)
    story_id = db.Column(db.Integer, db.ForeignKey('stories.id'), nullable=False)

    def to_dict(self):
        return{
            "id": self.id,
            "paragraph":self.paragraph,
        }
    
    def __repr__(self):
        return (f"<Paragraph id={self.id}, paragraph={self.paragraph} >")
