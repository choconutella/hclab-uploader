from threading import Thread, Event
from abc import ABCMeta, abstractclassmethod

class Service (Thread, metaclass=ABCMeta):

  def __init__(self):

    super().__init__()
    self._runner = Event()
    self._runner.set()


  @abstractclassmethod
  def run(self):
    """Start the service function"""

  def stop(self):
    self._runner.clear()

  def is_running(self):
    return True if self._runner.is_set() else False
    