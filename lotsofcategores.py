from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from models import Base, User, Category, Item


# Connect to Database and create database session
engine = create_engine('sqlite:///cagegory.db')
Base.metadata.bind = engine

DBSession = sessionmaker(bind=engine)
session = DBSession()

cat1 = Category(name='Soccer')
session.add(cat1)

cat2 = Category(name='Basketball')
session.add(cat2)

cat3 = Category(name='Baseball')
session.add(cat3)

cat4 = Category(name='Football')
session.add(cat4)

cat5 = Category(name='Skating')
session.add(cat5)

cat6 = Category(name='Snowboarding')
session.add(cat6)

session.commit()


# Create dummy user
User1 = User(name="Robo Barista", email="tinnyTim@udacity.com",
             picture='https://pbs.twimg.com/profile_images/2671170543/18debd694829ed78203a5a36dd364160_400x400.png')
session.add(User1)
session.commit()

item1 = Item(title="Stephen Curry",user_id=1,description="Stephen Curry (Stephen Curry), was born on March 14, 1988, in Akron, Ohio (Akron, Ohio), American professional basketball player, the secretary point guard, playing for the NBA golden state warriors.",category_id='2')
session.add(item1)

item1 = Item(title="Lebron James",user_id=1,description="Lebron james was born in 1974 .His mather gave birth to him at the age of 16.He joined the NBA when he was 18years old.But now,he has made great achievements in NBA.I think he has gone beyond KOBE,the greatest player in nba now.because he is younger and stronger than KOBE even he has not won the championship of NBA.",category_id='2')
session.add(item1)

session.commit()