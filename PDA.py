import re

def stacks():
	stack1 = []
	stack2 = []
	return stack1, stack2

class PDA_Controller:
	#"Setup" phase for stacks 
    def __init__(self):
        self.state = 'q0'
        self.stack1,self.stack2= stacks()
        
    
    def get_user_input(self):
        while True:
            user_text = input("Please enter a string (format: a's/b's/c's): ")
            if re.match(r"^a+/b+/c+$",user_text):
                return user_text
            else: 
                print("Invalid format! Please use 'a','/','b','/','c' in order.")
    
    
    def process(self,user_text):
         # Reset stacks for fresh processing+
         self.stack1.clear()
         self.stack2.clear()
         
         # Initialize stacks with bottom markers ('Z0')
         self.stack1.append('Z0')
         self.stack2.append('Z0')
         
         # PHASE 1: Header (a's)
         for char in user_text:
              if self.state == 'q0' and char=='a':
                   self.stack1.append('A')
              elif self.state == 'q0' and char == '/':
                   self.state ='q1'

         # PHASE 2: Payload (b's)
              elif self.state == 'q1'and char=='b':
                   if self.stack1[-1] == 'Z0':
                       return "we have extra b's!"
                   self.stack1.pop()
                   self.stack2.append('B')
              elif self.state == 'q1' and char == '/':
                     if self.stack1[-1] == 'Z0':
                      self.state ='q2'
                     else: return "that means we have extra A's!"
        # PHASE 3: Signature (c's)
              elif self.state == 'q2' and char=='c':
                   if self.stack2[-1] == 'Z0':
                       return " we have extra c's!"
                   else:self.stack2.pop()
              else:
                   return "Invalid character encountered!"
         if self.stack1[-1] == 'Z0' and self.stack2[-1] == 'Z0':
            return "String Accepted!"
         else:
            return "String Rejected"

if __name__ == "__main__":
    pda = PDA_Controller()
    user_input = pda.get_user_input()
    result = pda.process(user_input)
    print(result)
         