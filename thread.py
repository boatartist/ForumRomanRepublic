from exceptions import PermissionDenied
from sqlalchemy.orm import relationship, mapped_column, Mapped
from sqlalchemy import ForeignKey, DateTime
from base import Base
from typing import Optional
from sqlalchemy import select
from sqlalchemy.sql import func
from datetime import datetime
from user import User
from post import Post

class ThreadPostLink(Base):
  __tablename__ = "threadpostlink"
  threadid: Mapped[int] = mapped_column(ForeignKey("thread.id"), primary_key=True)
  postid: Mapped[int] = mapped_column(ForeignKey("post.id"), primary_key=True)
  def __init__(self, threadid, postid):
    self.threadid = threadid
    self.postid = postid

class Thread(Base):
  __tablename__ = "thread"
  
  id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
  title: Mapped[str]
  owner: Mapped[int]
  forum_id: Mapped[int]
  tags: Mapped[Optional[str]] = mapped_column(default=None)
  created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())
  first_post: Mapped[int] = mapped_column(ForeignKey("post.id"))

  def __init__(self, title, first_post, forum_id):
    self.title = title
    self.first_post = first_post.get_id()
    self.owner = first_post.get_author()
    self.forum_id = forum_id
    print(first_post)
    print(first_post.get_id())

  def get_owner(self):
    """
    Returns the owner of the thread.
    """
    return self.owner
  
  def get_id(self):
    return self.id 
  
  def get_title(self):
    """
    Returns the title of the thread.
    """
    return self.title
  
  def get_tags(self):
    """
    Returns a alphabetically sorted list of unique tags.
    """
    if not self.tags:
      return []
    return sorted(set(tag.strip() for tag in self.tags.split(",") if tag.strip()))
  
  def get_posts(self, session):
    """
    Returns a list of posts in this thread, in the order they were published.
    """
    query = select(ThreadPostLink).join(Post).where(ThreadPostLink.threadid == self.id).order_by(Post.date)
    return session.execute(query).scalars().all()
  
  def publish_post(self, post, session):
    """
    Adds the given post object into the list of posts.
    """
    print(f"PostID: {post.id}, PostDT: {post.date}")
    print(f"SelfID: {self.id}")
    query = select(ThreadPostLink).where(ThreadPostLink.threadid == self.id, ThreadPostLink.postid == post.id)
    existing = session.execute(query).scalar_one_or_none()

    if not existing:
      link = ThreadPostLink(threadid = self.id, postid=post.id)
      session.add(link)
  
  def remove_post(self, post, by_user, session):
    """
    Allows the given user to remove the post from this thread.
    Does nothing if the post is not in this thread.
    * raises PermissionDenied if the given user is not the author of the post.
    """
    if post.get_author() != by_user:
      raise PermissionDenied
    query = select(ThreadPostLink).where(ThreadPostLink.threadid == self.id).where(ThreadPostLink.postid == post.id)
    link = session.execute(query).scalar_one_or_none()
    if link:
      session.delete(link)
      return True
    return False



  def set_title(self, title, by_user):
    """
    Allows the given user to edit the thread title.
    * raises PermissionDenied if the given user is not the owner of the thread.
    """
  
    if self.get_owner() != by_user.get_id():
      raise PermissionDenied
    self.title = title
  
  def set_tags(self, tag_list, by_user):
    """
    Allows the given user to replace the thread tags (list of strings).
    * raises PermissionDenied if the given user is not the owner of the thread.
    """
    if self.get_owner() != by_user.get_id():
      raise PermissionDenied
    self.tags = ",".join(tag_list) if tag_list else None