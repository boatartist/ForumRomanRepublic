from base import Base
from sqlalchemy import select
from sqlalchemy.orm import Mapped
from sqlalchemy.orm import mapped_column
from thread import Thread
from post import Post

class Forum(Base):
  __tablename__ = 'forum'

  id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
  title: Mapped[str]
  def __init__(self, title='forum'):
    self.title = title

  def get_id(self):
    return self.id
  
  def get_title(self):
    return self.title

  def get_threads(self, session):
    """
    Returns a list of threads in the forum, in the order that they were published.
    """
    threads = session.execute(select(Thread).where(Thread.forum_id == self.id)).all()
    print(threads)
    print(threads[0].get_id())
    return threads
  
  def publish(self, title, first_post, author):
    """
    Creates a new thread with the given title and adds it to the forum.
    The content and author are provided to allow you to create the first post object.
    Forum threads are stored in the order that they are published.
    Returns the new thread.
    """
    thread = Thread(title, first_post, self.get_id())
    return thread
  
  def search_by_tag(self, tag):
    """
    Searches all forum threads for any that contain the given tag.
    Returns a list of matching thread objects in the order they were published. (currently works oldest -> newest)
    """
    matching_threads = []
    for thread in self.get_threads():
      tags = thread.get_tags()
      if tag in tags:
        matching_threads.append(thread)
    return matching_threads
  
  def search_by_author(self, author, session):
    """
    Searches all forum threads for posts by the given author.
    Returns a list of matching post objects in any order you like. (currently works oldest -> newest)
    """
    matching_posts = []
    for thread in self.get_threads(session):
      print(thread)
      print(type(thread))
      posts = thread.get_posts(session)
      print(posts)
      print(type(posts))
      for post in posts:
        post_author = post.get_author()
        if post_author == author.get_id():
          matching_posts.append(post)
    return matching_posts
