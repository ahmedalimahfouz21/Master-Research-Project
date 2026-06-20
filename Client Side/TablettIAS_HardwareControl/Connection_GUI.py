import zmq
import json


		
class Connection_Zmq:
	
	def __init__(self, ip, port):
		self.prevMessage = {}
		self.lastMessage = {}
		self.context = zmq.Context()
		self.socket = self.context.socket(zmq.REP)
		self.socket.bind("tcp://"+ip+":"+port)
	
	def check_for_message(self):
		message = None
		
		try:
			msg = self.socket.recv_string(flags = zmq.NOBLOCK)
			print("message from node on py: "+ str(msg))
			message = json.loads(str(msg))
			self.prevMessage = self.lastMessage
			self.lastMessage = message
			return message
		
		except zmq.Again as e:
			message = None
			return message
			print("No message from node")
		
		return message
		
	def answer_message_string(self, answer):
		self.socket.send_string(answer)
	
	def answer_message_json(self, answer):
		self.socket.send_string(json.dumps(answer))
		
	
			
if __name__ == "__main__":
	connGUI = Connection_Zmq("127.0.0.1","5555")
	while True:
		
		msg = connGUI.check_for_message()
		
		if msg is not None:
			connGUI.answer_message_string('{ "message" : "Hello Back"}')
