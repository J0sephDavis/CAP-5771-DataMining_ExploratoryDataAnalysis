from time import time as _time
class Stopwatch():
	''' class used to print time durations. '''
	start_time:float
	end_time:float
	def __init__(self):
		self.start_time=0
		self.end_time=0
	def start(self):
		self.start_time = _time()
	def end(self):
		self.end_time = _time()
	def __str__(self):
		seconds = self.end_time - self.start_time
		if seconds > 60:
			return f'{seconds:0.2f}s / {seconds/60:0.2f} minutes'
		else:
			return f'{seconds:0.2f}s'
