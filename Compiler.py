######################################################
###		   NASIOS VASILEIOS   A.M: 3296  cse63296  ###
###		   VAKALOS APOSTOLOS  A.M: 3185  cse63185  ###
######################################################

import sys

if len(sys.argv) < 2:
	print('Expected input filepath/filename')
	exit(-1)

filepath = sys.argv[1]

#### for lexical/syntax analyzer ####

filePointer = 0 	
line = 1
token = ''
reservedkeywords = {'if','while','doublewhile','loop','forcase','incase','declare','call','return','input','print','not','and','or','in','inout','program','else','procedure','function','when','default','exit'}
setofdeclarations = {'  '}
statementskeywords = {'if','while','doublewhile','loop','forcase','incase','call','return','input','print','exit'}

sett = {'{','}','(',')','/',':',':=',',','<','>','<>','+','-','*','>=','<=','[',']',';','='}

relational_op = {'<','>','<>','>=','<=','='}

# Hold the subprogram's names (id) 
identifiers = {'  '}

procedurenames = {'  '}


#### for intermediate code ####

# quads number
q = 0

# counter for temporary variables 'T_t'
t = 0

# Dictionary for quads
quads= {}

# Holds (subprogram id, type) WHERE type: function or procedure
subprogramstack = []

# Hold the subprograms names for begin - end block quads 
namestack = []

# subprogramdict explanation:
# key: subprogram name, value: [[parameter type,...],counter1,counter2] 
# WHERE parameter type = in/inout , counter1 = number of formal parameters, counter2 = number of actual parameters
subprogramDict = {} 

#### for final code	####

# SymbolTable explanation:
# key: subprogram name  value: [depth,framelength,{variable name:[offset,passtype]},father,startquad label]
# WHERE passtype = CV/REF	
symbolTable = {}

offsetCounter = 8
depth = 0

# Holds the final code instructions
Mips = []

# Used to detect if return statement missing
returnflagstack = [];


def nextquad():
	global q
	return q + 1

def genquad(op,x,y,z):
	global q
	q += 1
	quads.update({q:[op,x,y,z]})
	
def newtemp():
	global t
	t += 1
	return ('T_' + str(t))

def emptylist():
	return []

def makelist(x):
	return [x]

def merge(list1,list2):
	return list1+list2

def backpatch(list,z):
	for label in list:
		quads[label][3] = str(z) 	



########################################################

##			LEXICAL ANALYZER

########################################################

def lex():
	counter = 0	## keep the word length	

	global filePointer,line

	path = filepath[-4:]
	if path != '.min':
		print('Expected *.min file')
		return 'File error'
	file = open(filepath,"r")
	file.seek(filePointer)

	#state 0	
	char = file.read(1)
	while(char == ' ' or char == '\t' or char == '\n'):
		if char == '\n':
			line += 1

		filePointer += 1
		file.seek(filePointer)
		char = file.read(1)
	   
	# state 1
	if( (char >= 'a' and char <= 'z') or (char >= 'A' and char <= 'Z') ):
		startSeek = filePointer

		while(True):
			file.seek(filePointer)
			char = file.read(1)		

			if( (char >= 'a' and char <= 'z') or (char >= 'A' and char <= 'Z') or (char >= '0' and char <= '9') ):
				filePointer+=1
				counter+=1		
			else:
				finalSeek = filePointer
				file.seek(startSeek)
				string = file.read(counter)
				filePointer = finalSeek
				return string		
				
	#state 2
	elif (char >= '0' and char <= '9'):
		startSeek = filePointer

		checkdeclaration = 0
		while(True):
			
			file.seek(filePointer)
			char = file.read(1)

			if char>= '0' and char<= '9':
				filePointer += 1		
				counter += 1
				continue

			# case 2acsd => wrong
			if (char >= 'a' and char <= 'z') or (char >= 'A' and char <= 'Z'):
				checkdeclaration = 1
				filePointer += 1		
				counter += 1
		
			else:
				finalSeek = filePointer
				file.seek(startSeek)
				string = file.read(counter)
				filePointer = finalSeek
			
				if checkdeclaration == 1:
					print('line:' + str(line) + '  ' + string + ' => wrong declaration ')					
					return 'ERROR'
	
				return string

	# state 3	
	elif char == '{' or char == '}' or char == '(' or char == ')' or char == '[' or char == ']':
		filePointer += 1
		return char 

	# state 4
	elif char == '+' or char == '-' or char == '*':
		filePointer += 1

		if char == '*':
			file.seek(filePointer)
			nextchar = file.read(1)
			if nextchar == '/':
				filePointer += 1
				print('line:' + str(line) + '  close comment without open')
				return 'ERROR'
		return char 

	# state 5
	elif char == ',' or char == ';':
		filePointer+=1
		return char 

	# state 6
	elif char == ':':
		filePointer+=1
		file.seek(filePointer)
		nextchar  = file.read(1)
 
		if nextchar == '=' :
			filePointer += 1
			return ':='

		return char 

	# state 7	
	elif char == '<' :
		filePointer+=1
		file.seek(filePointer)
		nextchar = file.read(1)

		if nextchar == '=' :
			filePointer += 1
			return '<='

		elif nextchar == '>' :
			filePointer += 1
			return '<>'

		else:
			return char 

	elif char == '>' :
		filePointer += 1
		file.seek(filePointer)
		nextchar = file.read(1)

		if nextchar == '=' :
			filePointer += 1
			return '>='

		else:
			return char 

	# state 8
	elif char == '/' :
		filePointer += 1
		file.seek(filePointer)
		nextchar = file.read(1)

		if nextchar == '/' :

			while (True):
				filePointer += 1
				file.seek(filePointer)
				comments = file.read(1)
				if comments == '\n':
					return lex()

		if nextchar == '*':
			openline = line
			check = 0

			while True:      
				filePointer += 1
				file.seek(filePointer)
				closecomment = file.read(1)				

				if 	closecomment == '/' and check == 0:
					check = - 1
					continue
				if closecomment == '*' and check == -1:
					filePointer += 1
					print('line:' + str(line) + ' open comment in comment')
					return 'ERROR'
				if closecomment == '*' and check == 0:
					check = 1	
					continue	
				if closecomment == '/' and check == 1:
					filePointer += 1
					return lex()
				if closecomment == '':
					print('line:' + str(openline) + ' open comment without closed')
					return 'ERROR'
				else:
					if closecomment == '\n':
						line += 1	
					check = 0
		else:
			return char 

	# state 9
	elif char == '=':
		filePointer+=1
		file.seek(filePointer)
		nextchar  = file.read(1)
 
		if nextchar == '=' :
			print('line:' + str(line) + ' use \'=\' instead of \'==\'')
			return 'ERROR'
		else:
			return '='
			
	# state 10
	# case eof
	elif char == '':
		return char 
	else:
		print('line:' + str(line) + '   Symbol \''+char + '\' is not recognizable')
		return 'ERROR'

	file.close()


########################################################

##			SYNTAX ANALYZER

########################################################

def program():
	global token, depth

	if token == 'File error':
		return

	if token == 'program':
		token = lex()
		if token == 'ERROR':
			return 'ERROR'
		if not(token in reservedkeywords or token in sett or token.isnumeric() == True):   
			namestack.append(token)	
		
			symbolTable[token] = [depth,12,{},token,-1]
			identifiers.add(token)

			token = lex()
			if token == 'ERROR':
				return 'ERROR'
		else:
			print('line:'+str(line) + ' wrong program name')
			return 'ERROR'

		
		if token == '{':
			token = lex()
			if token == 'ERROR':
				return 'ERROR'
			if block() == 'ERROR':
				return 'ERROR IN PROGRAM'
			if token == '}':
				
				return 'Compile is correct'
			else:
				print('line:'+str(line)+ ' Main program bracket \'}\' missing')
				return 'ERROR'
		else:
			print('line:'+str(line)+' bracket \'{\' expected')
			return 'ERROR'

	else:
		return 'Keyword \'program\' expected' 


def block():
	global offsetCounter,depth,q

	if declarations() == 'ERROR':
		return 'ERROR'
	if subprograms() == 'ERROR':
		return 'ERROR'
	#case of wrong order in block
	if not(token in statementskeywords or token == '{' or token in setofdeclarations):
		
		print('line:'+str(line)+' Program or subprogram block must follow this structure with this order: { Declarations, Subprograms, Statements }')
		return 'ERROR'
		
	genquad('begin_block',namestack[-1],'_','_')
	symbolTable.get(namestack[-1])[4] = q			# Take the start quad number for symbol table
	
	if statements()	== 'ERROR':
		return 'ERROR'
		
	if len(namestack) == 1:
		genquad('halt','_','_','_')
	
	functionName = namestack[-1]
	symbolTable.get(functionName)[1] = offsetCounter+4
	
	genquad('end_block',namestack.pop(),'_','_')

	if len(namestack) >= 1:
		functionName = namestack[-1]
		offsetCounter = symbolTable.get(functionName)[1] 
		depth -= 1
	
	#case of wrong order in block
	if token != '}' and token != '':
		#case statement; is not acceptable
		if token == ';':
			print('line:'+str(line)+' Syntax error: \'' + token + '\'')
			print('\nHINT 1: For multiple statements use this structure: { statement ( ; statement )* }')
			print('HINT 2: If you want one statement semicolon is not needed at the end')
			return 'ERROR'
		print('line:'+str(line)+' Program or subprogram block must follow this structure with this order: { Declarations, Subprograms, Statements }')
		return 'ERROR'	


def declarations():
	global token
	
	#case program id { subprograms statements }
	if token == 'function' or token == 'procedure':
		return
 		
	if token == 'declare':
		token = lex()
		if token == 'ERROR':
			return 'ERROR'
		
		if  varlist() == 'ERROR':
			return 'ERROR'

		if token == ';':
			token = lex()
			if token == 'ERROR':
				return 'ERROR'
			return 	declarations()

		else:
			print('line:'+ str(line) + ' semicolon \';\' expected')
			return 'ERROR'
	else:
		#case program id { statements }
		if token in statementskeywords or token == '{' or token in setofdeclarations:
			return

		# case program id {  } 
		elif token == '}':
			print('line:'+ str(line) + ' Program needs at least one statement ')
			return 'ERROR'
 
		else:
			print('line:'+ str(line) + ' Syntax error expected function name or declaration or statement ')
			return 'ERROR'
		

def varlist():
	global token, offsetCounter

	while True:
		if token in reservedkeywords:
			print('line:' + str(line) + ' name \'' + token + '\' is reserved keyword')
			return 'ERROR'

		#case of number as variable name (isnumeric needs python3)
		if token.isnumeric() == True:
			print('line:' + str(line) + ' name \'' + token + '\' can not be variable name')
			return 'ERROR'

		#case declare ; 
		if token == ';':
			return

		# check id
		if not(token in sett) and not(token in reservedkeywords): 
		
			setofdeclarations.add(token)
			functionName = namestack[-1]
			variableDict =	symbolTable.get(functionName)[2]
			if token in variableDict:
				print('line:' + str(line) + ' subprogram \'' + functionName + '\' has 2 variables with the same name: \'' + token + '\'')
				return 'ERROR'
			offsetCounter += 4
			variableDict[token] = [offsetCounter]
			

			if len(token) > 30:
				print('line:' + str(line) + ' variable \'' + token + '\' must be smaller or equal than 30 charachers'  )
				return 'ERROR'
			token = lex()
			if token == 'ERROR':
				return 'ERROR'
			if token == ',':
				token = lex()
				if token == 'ERROR':
					return 'ERROR'
				if token == ';':
					print('line:'+ str(line) + ' instead of \',\' expected variable name')
					return 'ERROR'
				continue
			if token == ';':
				return
			else:
				print('line:'+ str(line) + ' instead of \'' + token + '\' semicolon ; or comma , expected' )
				return 'ERROR'
		else:
			print('line:' + str(line) + ' wait for variable name')
			return 'ERROR'


def subprograms():
	global token 
	if (subprogram() == 'ERROR'):
		return 'ERROR'


def subprogram():
	global token, offsetCounter, depth
	checkforprocedure = 0	

	if token in statementskeywords or token in setofdeclarations or token == '{':
		return

	if token == 'function' or token == 'procedure':
		if token == 'function':
			returnflagstack.append(1)

		if token == 'procedure':
			returnflagstack.append(0)
			checkforprocedure = 1

		token = lex()
		if token == 'ERROR':
			return 'ERROR'		

		if checkforprocedure == 1:
			procedurenames.add(token)		

		functionName = namestack[-1]
		symbolTable.get(functionName)[1] = offsetCounter
		
		if token in identifiers:
			print('line:' + str(line) + ' subprogram name \'' + token + '\' already exists in program above')
			return 'ERROR'

		subprogramDict[token] = [[],0,0]

		identifiers.add(token)
		namestack.append(token)
		
		offsetCounter = 8
		depth += 1
		symbolTable[token] = [depth,12,{},functionName,-1]

		if token == '(':
			print('line:' + str(line) + ' subprogram name missing')
			return 'ERROR'
		

		if not(token in reservedkeywords) and not(token in sett):
			token = lex()
			if token == 'ERROR':
				return 'ERROR'
			if funcbody() == 'ERROR':
				return 'ERROR'

			return subprogram()
		
		else:
			print('line:' + str(line) + ' subprogram name \'' + token + '\' can not be a reserved keyword or symbol')
			return 'ERROR'
	else:
		print('line:' + str(line) + ' expected keyword \'function\' or \'procedure\' or statement(s)')
		return 'ERROR'


def funcbody():
	global token, offsetCounter
	
	if formalpars() == 'ERROR':
		return 'ERROR'
	
	if token == '{':
		token = lex()
		if token == 'ERROR':
			return 'ERROR'
			
		#case subprogram id{}
		if token == '}':
			print('line:' + str(line) + ' subprogram expected at least one statement')
			return 'ERROR'
		if block() == 'ERROR':
			return 'ERROR'
		if token == '}':

			if returnflagstack[-1] == 1:
				print('line:' + str(line) + ' instead of \'' + token + '\' expected  \'return\'')
				print('HINT: Every function must have at least one return statement')
				return 'ERROR'
			returnflagstack.pop()

			token = lex()
			if token == 'ERROR':
				return 'ERROR'
			return
		else:
			print('line:' + str(line) + ' instead of \'' + token + '\' subprogram expected  \'}\'')
			return 'ERROR'
	else:
		print('line:' + str(line) + ' instead of \'' + token + '\' expected  \'{\'')
		return 'ERROR'
			

def formalpars():
	global token
	
	if token == '(':
		token = lex()
		if token == 'ERROR':
			return 'ERROR'
	
		if formalparlist() == 'ERROR':
			return 'ERROR'

		if token == ')':
			token = lex()
			if token == 'ERROR':
				return 'ERROR'
			return
	else:
		print('line:' + str(line) + ' instead of \'' + token + '\' expected  \'(\'')
		return 'ERROR'


def formalparlist():
	global token

	#case subprogram id(){  } no parameters
	if token == ')':
		return

	while True:
		if formalparitem() == 'ERROR':
			return 'ERROR'
		if token == ',':
			token = lex()
			if token == 'ERROR':
				return 'ERROR'
			continue
	
		elif token == ')':
			return 
		else:
			print('line:' + str(line) + ' instead of \'' + token + '\' expected comma \',\' and new parameter or \')\'  ')
			return 'ERROR'


def formalparitem():
	global token, offsetCounter

	parameterType = ""
	if token == 'in' or token == 'inout':
		if token == 'in':
			parameterType = 'CV'
			functionName = namestack[-1]
			subprogramDict.get(functionName)[0].append('in')
			subprogramDict.get(functionName)[1] += 1
		else:
			parameterType = 'REF'
			functionName = namestack[-1]
			subprogramDict.get(functionName)[0].append('inout')
			subprogramDict.get(functionName)[1] += 1

		token = lex()
		if token == 'ERROR':
			return 'ERROR'
		if  not(token in reservedkeywords) and not(token in sett):
			setofdeclarations.add(token)	

			functionName = namestack[-1]
			variableDict =	symbolTable.get(functionName)[2]
			if token in variableDict:
				print('line:' + str(line) + ' subprogram \'' + functionName + '\' has 2 parameters with the same name: \'' + token + '\'')
				return 'ERROR'
			offsetCounter += 4
			variableDict[token] = [offsetCounter,parameterType]
				
			token = lex()
			if token == 'ERROR':
				return 'ERROR'
			return 
		else:
			print('line:' + str(line) + ' parameter name \'' + token + '\' can not be a reserved keyword or symbol')
			return 'ERROR'
	else:
		print('line:' + str(line) + ' expected \'in\' or \'inout\' keywords instead of \'' + token + '\'')
		return 'ERROR'


def statements():
	
	global token

	if token in statementskeywords or token in setofdeclarations:
		if statement() == 'ERROR':
			return 'ERROR'

	#case { statement (;statement)*}
	elif token == '{':
		token = lex()
		if token == 'ERROR':
				return 'ERROR'

		if token == '}':
			print('line:' + str(line) + ' expected at least one statement between  \' { ... } \'')
			return 'ERROR' 

		while True:			
			if statement() == 'ERROR':
				return 'ERROR'
			elif token == ';':
				token = lex()
				if token == 'ERROR': return 'ERROR'
				if token == '}':
					print('line:' + str(line) + ' found \';\' wihtout statement afterwards')
					return 'ERROR'
				continue
			elif token == '}':
				token = lex()
				if token == 'ERROR':
					return 'ERROR'
				return 
			else:
				print('line:' + str(line) + ' instead of \''+ token + '\' expected \'}\' or \';\' and another statement')
				return 'ERROR'
	
	else:
		print('line:' + str(line) + ' instead of \''+ token + '\'  expected statement or { statement ( ; statement )* }')
		print('\nHINT: If you want to make assignment make sure variable name is declared')		
		return 'ERROR'


def statement():
	global token, exp

	if token == 'if':
		token = lex()
		if token == 'ERROR': return 'ERROR'		
		if if_stat() == 'ERROR': return 'ERROR'
		return
	
	if token == 'while':
		token = lex()
		if token == 'ERROR': return 'ERROR'	
		if while_stat() == 'ERROR': return 'ERROR'
		return

	if token == 'doublewhile':
		token = lex()
		if token == 'ERROR': return 'ERROR'
		if doublewhile_stat() == 'ERROR': return 'ERROR'
		return

	if token == 'loop':
		token = lex()
		if token == 'ERROR': return 'ERROR'
		if loop_stat() == 'ERROR': return 'ERROR'
		return

	if token == 'exit':
		token = lex()
		if token == 'ERROR': return 'ERROR'
		if exit_stat() == 'ERROR': return 'ERROR'
		return

	if token == 'forcase':
		token = lex()
		if token == 'ERROR': return 'ERROR'
		if forcase_stat() == 'ERROR': return 'ERROR'	
		return

	if token == 'incase':
		token = lex()
		if token == 'ERROR': return 'ERROR'
		if incase_stat() == 'ERROR': return 'ERROR'
		return

	if token == 'call':
		token = lex()
		if token == 'ERROR': return 'ERROR'
		if call_stat() == 'ERROR': return 'ERROR'
		return

	if token == 'return':
		returnflagstack[-1] = 0
		token = lex()
		if token == 'ERROR': return 'ERROR'
		if return_stat() == 'ERROR': return 'ERROR'
		return

	if token == 'input':
		token = lex()
		if token == 'ERROR': return 'ERROR'
		if input_stat() == 'ERROR': return 'ERROR'
		return

	if token == 'print':
		token = lex()
		if token == 'ERROR': return 'ERROR'
		if print_stat() == 'ERROR': return 'ERROR'
		return

	if token in setofdeclarations:
		id = token
		token = lex()
		if token == 'ERROR': return 'ERROR'
		
		retassignmentstat = assignment_stat()
		if retassignmentstat == 'ERROR': return 'ERROR'
		genquad(':=',retassignmentstat,'_',id)
		
		return
	if token in identifiers:
		print('line:' + str(line) + ' function \''+ token + '\' can not be assigned')
		return 'ERROR'


def if_stat():
	global token
	truelist  = []
	falselist = []
	iflist = []

	if token == '(':
		token = lex()
		if token == 'ERROR': return 'ERROR'
		
 		#case if () => no conditions
		if token == ')':
			print('line:' + str(line) + ' expected boolean expression between \'if( ... )\'')
			return 'ERROR'

		retcondition = condition()
		if retcondition == 'ERROR': return 'ERROR'
		if token == ')':
			token = lex()
			if token == 'ERROR': return 'ERROR'
			if token == 'then':
			
				truelist = retcondition[0]
				falselist = retcondition[1]
				backpatch(truelist,nextquad())

				token = lex()
				if token == 'ERROR': return 'ERROR'
				if statements() == 'ERROR': return 'ERROR'
				
				iflist = makelist(nextquad())				
				genquad('jump','_','_','_')			
				backpatch(falselist,nextquad())
				
				if else_part() == 'ERROR': return 'ERROR'
				
				backpatch(iflist,nextquad())

			else:
				print('line:' + str(line) + ' instead of \''+ token + '\' expected \'then\' keyword')
				return 'ERROR'			
		else:
			print('line:' + str(line) + ' instead of \''+ token + '\' expected \')\'')
			return 'ERROR'
	else:
		print('line:' + str(line) + ' instead of \''+ token + '\' expected \'(\'')
		return 'ERROR'


def else_part():
	global token
	
	oldline = line ## helps in messages	

	if token == 'else':
		token = lex()
		if token == 'ERROR': return 'ERROR'
		# case else without statements
		if token in statementskeywords or token in setofdeclarations or token == '{':
			if statements() == 'ERROR': return 'ERROR'
		else:
			print('line:' + str(oldline) + ' after \'else\' expected statement or { statement ( ; statement )* }')
			return 'ERROR'

	# case no else part
	elif token == ';' or token == '}':
		return 
	else:
		print('line:' + str(line) + ' instead of \''+ token + '\' expected \'else\' part or semicolon \';\' and another statement or \'}\'')
		return 'ERROR'


def condition():
	global token

	retboolterm = boolterm()
	if retboolterm == 'ERROR': return 'ERROR'
	truelist = retboolterm[0] 
	falselist = retboolterm[1]

	while True:
		if token == 'or':
		
			backpatch(falselist,nextquad())
			
			token = lex()
			if token == 'ERROR': return 'ERROR'
			
			retboolterm = boolterm()
			if retboolterm == 'ERROR': return 'ERROR'
			truelist = merge(truelist,retboolterm[0])
			falselist = retboolterm[1]
			continue
		
		#case e in  (or boolterm)*	
		elif token == ')' or token == ']' or token == 'and' or token == 'or':
			return [truelist,falselist]
		else:
			print('line:' + str(line) + ' instead of \''+ token + '\' expected \')\' or another boolean expression {or,and}')
			return 'ERROR'


def boolterm():
	global token

	returnboolfactor = boolfactor()
	if  returnboolfactor == 'ERROR': return 'ERROR'
	truelist  = returnboolfactor[0]
	falselist = returnboolfactor[1]

	while True:
		if token == 'and':
			backpatch(truelist, nextquad())
			token = lex()
			if token == 'ERROR': return 'ERROR'

			returnboolfactor = boolfactor()
			if returnboolfactor == 'ERROR': return 'ERROR'
			falselist = merge(falselist, returnboolfactor[1])
			truelist = returnboolfactor[0]
			continue

		#case e in  (and boolfactor)*	
		elif token == ')' or token == ']' or token == 'and' or token == 'or':
			return [truelist,falselist]

		else:
			print('line:' + str(line) + ' instead of \''+ token + '\' expected \')\' or another boolean expression {or,and}')
			return 'ERROR'	


def boolfactor():
	global token,exp
	falselist = []
	truelist  = []

	if token == 'not':
		token = lex()
		if token == 'ERROR': return 'ERROR'
		if token == '[':
			token = lex()
			if token == 'ERROR': return 'ERROR'

			#case not [ ] => no condition
			if token == ']':
				print('line:' + str(line) + ' expected boolean expression between \'[ ]\'')
				return 'ERROR'			

			retcondition = condition()
			if retcondition == 'ERROR': return 'ERROR'
			if token == ']':
				truelist = retcondition[0]
				falselist = retcondition[1] 
				token = lex()
				if token == 'ERROR': return 'ERROR'
				return [falselist,truelist]
			else:
				print('line:' + str(line) + ' instead of \''+ token + '\' expected \']\'')
				return 'ERROR'
		else:
			print('line:' + str(line) + ' after \'not\'  expected \'[\'')
			return 'ERROR'
	
	elif token == '[':
		token = lex()
		if token == 'ERROR': return 'ERROR'

		#case [ ] => no condition
		if token == ']':
			print('line:' + str(line) + ' expected boolean expression between \'[ ]\'')
			return 'ERROR'

		retcondition = condition()
		if retcondition == 'ERROR': return 'ERROR'
		if token == ']':
			token = lex()
			if token == 'ERROR': return 'ERROR'
			return retcondition
		else:
			print('line:' + str(line) + ' instead of \''+ token + '\' expected \']\'')
			return 'ERROR'

	elif token == '+' or token == '-' or token in setofdeclarations or token == '(' or token in identifiers or token.isnumeric() == True:
		retexpression = expression()		
		if retexpression == 'ERROR': return 'ERROR'
		x = retexpression			
		op = token
		
		if relational_oper() == 'ERROR': return 'ERROR'
		 
		retexpression = expression()		
		if retexpression == 'ERROR': return 'ERROR'
		y = retexpression

		truelist = makelist(nextquad())
		genquad(op,x,y,'_')
		falselist = makelist(nextquad())
		genquad('jump','_','_','_')
		
		return [truelist,falselist]
	else:
		print('line:' + str(line) + ' instead of \''+ token + '\' expected \'not [ ...condition... ]\' or \'[ ...condition... ]\' or \' <expression> <relational> <expression> \'') 
		return 'ERROR'


def expression():
	global token, exp, offsetCounter
	op = None
	x = None
	y = None
	t = None
	t2 = None

	retoptionalsign = optional_sign()
	if retoptionalsign == 'ERROR': return 'ERROR'
	
	returnterm = term()
	if returnterm == 'ERROR': return 'ERROR'
	x = returnterm

	if retoptionalsign == '+':
		t2 = newtemp()
	
		functionName = namestack[-1]
		variableDict =	symbolTable.get(functionName)[2]
		offsetCounter += 4
		variableDict[t2] = [offsetCounter]

		genquad('*','1',x,t2)
		x =  t2
	if retoptionalsign == '-':
		t2 = newtemp()

		functionName = namestack[-1]
		variableDict =	symbolTable.get(functionName)[2]
		offsetCounter += 4
		variableDict[t2] = [offsetCounter]

		genquad('*','-1',x,t2)
		x = t2
	
	#case e in ( <add-oper> <term>)*
	if token != '+' and token != '-':
		return x

	while True:
		if token == '+' or token == '-':
			op = token
			
			if add_oper() == 'ERROR': return 'ERROR'
			
			returnterm = term()
			if returnterm == 'ERROR': return 'ERROR'
			y = returnterm
			t = newtemp()

			functionName = namestack[-1]
			variableDict =	symbolTable.get(functionName)[2]
			offsetCounter += 4
			variableDict[t] = [offsetCounter]

			genquad(op,x,y,t)
			x = t
			continue
	
		elif token in relational_op or token == ')' or token == ']' or token == 'and' or token == 'or' or token == ';' or token == '}' or token == ',' or token == 'else' or token == 'default'  or token == 'when':				
			return t
		else:
			print('line:' + str(line) + ' instead of \''+ token + '\' expected sign {+,-} or relational operator {<,>,<>,>=,<=,=} or \'and\' or \'or\' or \'}\' or \';\' and new statement')
			return 'ERROR'


def relational_oper():
	global token
	if token in relational_op:
		token = lex()
		if token == 'ERROR': return 'ERROR'
		return
	else:
		print('line:' + str(line) + ' instead of \''+ token + '\' expected relational operator {<,>,<>,>=,<=,=}')
		print('\nHINT: use \'( ... )\' for arithmetic expressions or \'[ ... ]\' for boolean expressions \n')
		return 'ERROR'


def optional_sign():
	global token, exp
	ret = None	

	if token == '+' or token == '-':
		ret = token
		if add_oper() == 'ERROR': return 'ERROR'
		return ret

	elif token in setofdeclarations or token == '(' or token in identifiers or token.isnumeric() == True:		
		return
	
	elif not(token in identifiers):
		print('line:' + str(line) + ' subprogram or variable  name \''+ token + '\' doesn\'t exists')
		return 'ERROR'

	elif not(token in setofdeclarations):
		print('line:' + str(line) + ' subprogram or variable  name \''+ token + '\' doesn\'t exists')
		return 'ERROR'

	else:
		print('line:' + str(line) + ' instead of \''+ token + '\' expected sign {+,-} or numeric constant or \'( ...expression... )\' or subprogram id or variable name')
		return 'ERROR'


def add_oper():
	global token
	token = lex()
	if token == 'ERROR': return 'ERROR'
	return


def mul_oper():
	global token
	operator = ''	
	
	if token == '*' or token == '/':
		operator = token
		token = lex()
		if token == 'ERROR': return 'ERROR'
		return operator
	else:
		print('line:' + str(line) + ' instead of \''+ token + '\' expected operator {*,/}')
		return 'ERROR'	


def term():
	global token, exp, offsetCounter
	op = None
	x = None
	y = None
	t = None 
	
	retfactor = factor()
	if retfactor == 'ERROR': return 'ERROR'
	x = retfactor	

	if token != '*' and token != '/':
		return x

	while True:
		if token == '*' or token == '/':
			op = token
			
			if mul_oper() == 'ERROR': return 'ERROR'
			
			retfactor = factor()
			if retfactor == 'ERROR': return 'ERROR'
			y = retfactor 
			t = newtemp()
			
			functionName = namestack[-1]
			variableDict =	symbolTable.get(functionName)[2]
			if token in variableDict:
				print('line:' + str(line) + ' subprogram \'' + functionName + '\' has 2 variables with the same name: \'' + token + '\'')
				return 'ERROR'
			offsetCounter += 4
			variableDict[t] = [offsetCounter]

			genquad(op,x,y,t)
			x = t
			
			if token == '*' or token == '/':
				continue
		#case e in (<mul-oper> <factor>)*
		elif token == '+' or token == '-' or token in relational_op or token == ')' or token == ']' or token == 'and' or token == 'or' or token == '}' or token == ';' or token == ',' or token == 'else' or token == 'default' or token == 'when':
			return t

		else:	
			print(token)		
			print('line:' + str(line) + ' instead of \''+ token + '\' expected operator {*,/} or {+,-} or \')\' relational operator {<,>,<>,>=,<=,=} or \'and\' or \'or\' or \'}\' or \';\' and new statement')
			return 'ERROR'


def factor():
	global token,exp
	constant = 0	

	if token.isnumeric() == True:

		if int(token) < -32767 or int(token) > 32767:
			print('line:' + str(line) + ' constant \''+ token + '\' must be between [-32767,32767]')
			return 'ERROR'
		constant = token
		token = lex()
		if token == 'ERROR': return 'ERROR'
		return constant
		
	elif token == '(':
		token = lex()
		if token == 'ERROR': return 'ERROR'

		#case ( ) => no expression
		if token == ')':
			print('line:' + str(line) + ' expected arithmetic expression between \'( )\'')
			return 'ERROR'

		retexpression = expression()
		if retexpression == 'ERROR': return 'ERROR'
		if token == ')':
			token = lex()
			if token == 'ERROR': return 'ERROR'
			return retexpression
			
		else:
			print('line:' + str(line) + ' instead of \''+ token + '\' expected operator {+,-,*,/} or \')\'')
			print('\nHINT: use \'( ... )\' for arithmetic expressions or \'[ ... ]\' for boolean expressions \n')
			return 'ERROR'

	elif token in identifiers or token in setofdeclarations:
		ret = None
		flag = 0	# if we call a function, flag = 1
		
		if token in setofdeclarations:
			ret = token
			
		if token in identifiers:
			if token in procedurenames:
				print('line:' + str(line) + ' there is no function with \'' + token +'\' name')
				print('HINT: In expressions use functions instead of procedures')
				return 'ERROR'

			flag = 1
			subprogramstack.append((token,'function'))
			
		token = lex()
		if token == 'ERROR': return 'ERROR'
		
		retidtail = idtail()
		if retidtail == 'ERROR': return 'ERROR'
		
		if flag == 1: #function case
			if retidtail != None:
				ret = retidtail
		return ret

	else:
		print('line:' + str(line) + ' instead of \''+ token + '\' expected numeric constant or \'( ...expression... )\' or subprogram id or variable name')
		return 'ERROR'	

		
def idtail():
	global token
	
	if token == '(':
		token =lex()
		if token == 'ERROR': return 'ERROR'
		
		retactualpars = actualpars()
		if retactualpars == 'ERROR': return 'ERROR'
		return retactualpars
		
	#case e => nothing
	elif token == '*' or token == '/' or token == '+' or token == '-' or token in relational_op or token == ')' or token == ']' or token == ',' or token == '}' or token == ';':
		return
	else:
		print('line:' + str(line) + ' instead of \''+ token + '\' expected \'(\' or some arithmetic or relational operator {+,-,*,/,<,>,<>,=,>=,<=}')
		return 'ERROR'


def actualpars():
	global token, offsetCounter
	w = None
	t = subprogramstack[-1] 

	# case subprogram id () => no parameters
	if token == ')':

		name = subprogramstack[-1][0]
		callNumberOfFunctionParameters =  subprogramDict.get(name)[2]
		totalNumberOfFunctionParameters =  subprogramDict.get(name)[1]

		c1 = callNumberOfFunctionParameters
		c2 = totalNumberOfFunctionParameters

		if c1 < c2:
			print('line:' + str(line) + ' Subprogram ' + name + ' has ' + str(c2) + ' parameters instead of ' + str(c1))
			return 'ERROR'

		if t[1] == 'function':
			w = newtemp()
			functionName = namestack[-1]
			variableDict =	symbolTable.get(functionName)[2]
			offsetCounter += 4
			variableDict[w] = [offsetCounter]
			genquad('par',w,'RET','_')
			
		genquad('call',t[0],'_','_') # i have procedure
		subprogramstack.pop()
		
		token = lex()
		if token == 'ERROR': return 'ERROR'
		return w

	# token is given from idtail
	if actualparlist() == 'ERROR': return 'ERROR'
	if token == ')':
	
		if t[1] == 'function':
			w = newtemp()
			functionName = namestack[-1]
			variableDict =	symbolTable.get(functionName)[2]
			offsetCounter += 4
			variableDict[w] = [offsetCounter]
			genquad('par',w,'RET','_')
		
		genquad('call',t[0],'_','_') 
		subprogramstack.pop()
		
		token = lex()
		if token == 'ERROR': return 'ERROR'
		return w 
	else:	
		print('line:' + str(line) + ' instead of \''+ token + '\' expected \')\'')
		return 'ERROR'


def actualparlist():
	global token
	
	quad = []		# used to hold the quad from actualparitem to genquad it

	retactualparitem = actualparitem()
	if retactualparitem == 'ERROR': return 'ERROR'
	quad.append(retactualparitem)

	while True:
		if token == ',':
			token = lex()
			if token == 'ERROR': return 'ERROR'
			
			retactualparitem = actualparitem()
			if retactualparitem == 'ERROR': return 'ERROR'
			quad.append(retactualparitem)
			
			continue
		elif token == ')':
			for i in quad:
				genquad(i[0],i[1],i[2],i[3])
			
			name = subprogramstack[-1][0]
			callNumberOfFunctionParameters =  subprogramDict.get(name)[2]
			totalNumberOfFunctionParameters =  subprogramDict.get(name)[1]

			c1 = callNumberOfFunctionParameters
			c2 = totalNumberOfFunctionParameters

			if c1 < c2:
				print('line:' + str(line) + ' Subprogram ' + name + ' has ' + str(c2) + ' parameters instead of ' + str(c1))
				return 'ERROR'

			subprogramDict.get(name)[2] = 0
			return
		else:
			print('line:' + str(line) + ' instead of \''+ token + '\' expected keyword \'in\' or \'inout\' or \')\'')
			return 'ERROR'


def actualparitem():
	global token, exp

	subprogramName = subprogramstack[-1][0]
	counter  = subprogramDict.get(subprogramName)[2]
	counter2 = subprogramDict.get(subprogramName)[1]

	if (counter+1) > counter2:
		print('line:' + str(line) + ' Subprogram ' + subprogramName + ' has ' + str(counter2) + ' parameters instead of ' + str(counter+1))
		return 'ERROR'

	if token == 'in':		
		if subprogramDict.get(subprogramName)[0][counter] != 'in':
			number = counter + 1			
			print('line:' + str(line) + ' In subprogram '+subprogramName+ ' the #' + str(number) + ' parameter must be \'inout\' instead of \'in\'' )
			return 'ERROR'

		subprogramDict.get(subprogramName)[2] += 1

		token = lex()
		if token == 'ERROR': return 'ERROR'
		
		retexpression = expression()
		if retexpression == 'ERROR': return 'ERROR'
		quad = ['par',retexpression,'CV','_']

		return quad

	elif token == 'inout':
		
		if subprogramDict.get(subprogramName)[0][counter] != 'inout':
			number = counter + 1			
			print('line:' + str(line) + ' In subprogram '+subprogramName+ ' the #' + str(number) + ' parameter must be \'in\' instead of \'inout\'' )
			return 'ERROR'

		subprogramDict.get(subprogramName)[2] += 1

		token = lex()
		if token == 'ERROR': return 'ERROR'
		if token in setofdeclarations:
		
			quad = ['par',token,'REF','_']
			token = lex()
			if token == 'ERROR': return 'ERROR'
			return quad
		else:
			print('line:' + str(line) + ' \''+ token + '\' does not match with any declared variable')
			return 'ERROR'
	else:
		print('line:' + str(line) + ' instead of \''+ token + '\' expected keyword \'in\' or \'inout\' or \')\'')
		return 'ERROR'


def exit_stat():
	return


def assignment_stat():
	global token

	if token == ':=':
		token = lex()
		if token == 'ERROR': return 'ERROR' 
	else:
		print('line:' + str(line) + ' instead of \''+ token + '\' expected assignment operator \':=\'')
		return 'ERROR'
		
	retexpression = expression()
	if retexpression == 'ERROR': return 'ERROR'
	return retexpression


def while_stat():
	global token
	truelist  = []
	falselist = []

	Bquad = nextquad()
	if token == '(':
		token = lex()
		if token == 'ERROR': return 'ERROR'
		
		retcondition = condition()
		if retcondition == 'ERROR': return 'ERROR'

		truelist  = retcondition[0]
		falselist = retcondition[1]		

		if token == ')':			
			backpatch(truelist,nextquad())

			token = lex()
			if token == 'ERROR': return 'ERROR'
			if statements() == 'ERROR': return 'ERROR'
			
			genquad('jump','_','_',str(Bquad))
			backpatch(falselist,nextquad())
			return
		else:
			print('line:' + str(line) + ' instead of \''+ token + '\' expected  \')\'')
			return 'ERROR'
	else:
		print('line:' + str(line) + ' instead of \''+ token + '\' expected  \'(\'')
		return 'ERROR'


def doublewhile_stat():
	global token

	if token == '(':
		token = lex()
		if token == 'ERROR': return 'ERROR'
		if condition() == 'ERROR': return 'ERROR'
		if token == ')':
			token = lex()
			if token == 'ERROR': return 'ERROR'
			if statements() == 'ERROR': return 'ERROR'
			if token == 'else':
				token = lex()
				if token == 'ERROR': return 'ERROR'
				if statements() == 'ERROR': return 'ERROR'
				return
			else:
				print('line:' + str(line) + ' instead of \''+ token + '\' expected keyword \'else\'')
				return 'ERROR'
		else:
			print('line:' + str(line) + ' instead of \''+ token + '\' expected  \')\'')
			return 'ERROR'
	else:
		print('line:' + str(line) + ' instead of \''+ token + '\' expected  \'(\'')
		return 'ERROR'


def loop_stat():
	if statements() == 'ERROR': return 'ERROR'
	return
	

def forcase_stat():
	global token
	truelist  = []
	falselist = []
	first_quad = 0
	t = ''
	
	first_quad = nextquad()

	while(True):
		if token == 'default':
			break
		if token == 'when':
			token = lex()
			if token == 'ERROR': return 'ERROR'
			if token == '(':
				token = lex()
				if token == 'ERROR': return 'ERROR'
				
				retcondition = condition()
				if retcondition == 'ERROR': return 'ERROR'
				if token == ')':
				
					truelist = retcondition[0]
					falselist = retcondition[1]
					backpatch(truelist,nextquad())
					
					token = lex()
					if token == 'ERROR': return 'ERROR'
					if token == ':':
						token = lex()
						if token == 'ERROR': return 'ERROR'
						if statements() == 'ERROR': return 'ERROR'

						genquad('jump','_','_',str(first_quad))	
						backpatch(falselist,nextquad())
							
					else:
						print('line:' + str(line) + ' instead of \''+ token + '\' expected  \':\'')
						return 'ERROR'
				else:
					print('line:' + str(line) + ' instead of \''+ token + '\' expected  \')\'')
					return 'ERROR'
			else:
				print('line:' + str(line) + ' instead of \''+ token + '\' expected  \'(\'')
				return 'ERROR'
		else:
			print('line:' + str(line) + ' instead of \''+ token + '\' expected  keyword \'when\' or \'default\'')
			return 'ERROR'

	if token == 'default':
		token = lex()
		if token == 'ERROR': return 'ERROR'
		if token == ':':
			token = lex()
			if token == 'ERROR': return 'ERROR'
			if statements() == 'ERROR': return 'ERROR'		
			return
		else:
			print('line:' + str(line) + ' instead of \''+ token + '\' expected  \':\'')
			return 'ERROR'

	else:
		print('line:' + str(line) + ' instead of \''+ token + '\' expected keyword \'when\' or \'default:\'')
		print('\nHINT: forcase must have one \'default\' case')
		return 'ERROR'


def incase_stat():	
	global token
	
	if token == 'when':
		token = lex()
		if token == 'ERROR': return 'ERROR'
		if token == '(':
			token = lex()
			if token == 'ERROR': return 'ERROR'
			if condition() == 'ERROR': return 'ERROR'
			if token == ')':
				token = lex()
				if token == 'ERROR': return 'ERROR'
				if token == ':':
					token = lex()
					if token == 'ERROR': return 'ERROR'
					if statements() == 'ERROR': return 'ERROR'					
					if token == 'when':	
						# case ( when (<condition>) : <statements> )*	
						return incase_stat()
					else:
						return
				else:
					print('line:' + str(line) + ' instead of \''+ token + '\' expected  \':\'')
					return 'ERROR'
			else:
				print('line:' + str(line) + ' instead of \''+ token + '\' expected  \')\'')
				return 'ERROR'
		else:
			print('line:' + str(line) + ' instead of \''+ token + '\' expected  \'(\'')
			return 'ERROR'
	else:
		return


def return_stat():
	retexpression = expression()		
	if retexpression == 'ERROR': return 'ERROR'
	genquad('retv',retexpression,'_','_')
	return


def call_stat():
	global token

	if token in identifiers:
		if token not in procedurenames:
			print('line:' + str(line) + ' there is no procedure with \'' + token + '\' name')
			print('HINT: Call statement waits for procedure')
			return 'ERROR'			

		subprogramstack.append((token,'procedure'))
		
		token = lex()
		if token == 'ERROR': return 'ERROR'
		if token == '(':
			token =lex()
			if token == 'ERROR': return 'ERROR'
			if actualpars() == 'ERROR': return 'ERROR'
		else:
			print('line:' + str(line) + ' instead of \''+ token + '\' expected  \'(\'')
			return 'ERROR'
	else:
		print('line:' + str(line) + ' procedure name \''+ token + '\' does not exist')
		return 'ERROR'


def print_stat():
	global token

	if token == '(':
		token = lex()
		if token == 'ERROR': return 'ERROR'
		
		retexpression = expression()		
		if retexpression == 'ERROR': return 'ERROR'
		genquad('out',retexpression,'_','_')
		
		if token ==')':
			token = lex()
			if token == 'ERROR': return 'ERROR'
			return
		else:
			print('line:' + str(line) + ' instead of \''+ token + '\' expected  \')\'')
			return 'ERROR'
	else:
		print('line:' + str(line) + ' instead of \''+ token + '\' expected  \'(\'')
		return 'ERROR'
	

def input_stat():
	global token

	if token == '(':
		token = lex()
		if token == 'ERROR': return 'ERROR'
		if token in setofdeclarations:
		
			idname = token
			
			token = lex()
			if token == 'ERROR': return 'ERROR'
			if token ==')':
			
				genquad('inp',idname,'_','_')
				
				token = lex()
				if token == 'ERROR': return 'ERROR'
				return
			else:
				print('line:' + str(line) + ' instead of \''+ token + '\' expected  \')\'')
				return 'ERROR'
		else:
			print('line:' + str(line) + ' variable name \''+ token + '\' does not exist')
			return 'ERROR'
	else:
		print('line:' + str(line) + ' instead of \''+ token + '\' expected  \'(\'')
		return 'ERROR'


##################################################

###			FINAL

##################################################


def gnvlcode(v,functioname):
	function = symbolTable.get(functioname)
	parent = function[3]

	offset = -1
	counter = 0
	while(True):		
		if v in symbolTable.get(parent)[2].keys():
			break
		if parent == symbolTable.get(parent)[3]:
			print('Function \'' + functioname + '\' has no access to variable \'' + v +'\'')
			return 'ERROR'
		parent = symbolTable.get(parent)[3]
		counter += 1
		
	Mips.append("lw $t0,-4($sp)")
	for i in range(counter):		
		Mips.append("lw $t0,-4($t0)")
	offset = symbolTable.get(parent)[2].get(v)[0]
	Mips.append('addi $t0,$t0,-'+str(offset))
	return parent


def loadvr(v,r,functioname):
	reg = r
	variables = symbolTable.get(functioname)[2]
	vartable = variables.get(v)
	offset = -1
	
	sign = ""
	if v[0] == '-':
		sign = v[0]
		v = v[1:] 
	if v.isnumeric():
		Mips.append('li '+reg+','+ sign + str(v))
		
	# variable in the same nesting level
	elif v in variables.keys():		
		offset = vartable[0] 
		if len(vartable) == 2 and vartable[1] == 'REF':
			Mips.append('lw $t0,-'+str(offset)+'($sp)')
			Mips.append('lw '+reg+',-0($t0)')
		else:	
			Mips.append('lw '+reg+',-'+str(offset)+'($sp)')
	
	# variable in lower nesting level
	elif v not in variables.keys():
		predecesor = gnvlcode(v,functioname)
		if predecesor == 'ERROR':
			print('loadvr error')
			return 'ERROR'
		variables = symbolTable.get(predecesor)[2]
		vartable = variables.get(v)
		
		if len(vartable) == 2 and vartable[1] == 'REF': 
			Mips.append('lw $t0,-0($t0)')
			Mips.append('lw '+reg+',-0($t0)')
		else:
			Mips.append('lw '+reg+',-0($t0)')
	
	else:
		print('loadvr something is wrong!')
		return "ERROR"


def storerv(r,v,functioname):
	reg = r
	variables = symbolTable.get(functioname)[2]
	vartable = variables.get(v)
	offset = -1
	
	# variable in the same nesting level
	if v in variables.keys():
		offset = vartable[0]
		if len(vartable) == 2 and vartable[1] == 'REF':
			Mips.append('lw $t0,-'+str(offset)+'($sp)')
			Mips.append('sw '+reg+',-0($t0)')
		else:
			Mips.append('sw '+reg+',-'+str(offset)+'($sp)')
			
	# variable in lower nesting level
	elif v not in variables.keys():
		predecesor = gnvlcode(v,functioname)
		if predecesor == "ERROR":
			print('store error')
			return "ERROR"
		variables = symbolTable.get(predecesor)[2]
		vartable = variables.get(v)
		
		if len(vartable) == 2 and vartable[1] == 'REF': 
			Mips.append('lw $t0,-0($t0)')
			Mips.append('sw '+reg+',-0($t0)')
		else:
			Mips.append('sw '+reg+',-0($t0)')
	
	else:
		print('storerv something is wrong!')
		return "ERROR"
	

def finalcode():
	quad = []
	functioname = ''
	parflag = 0
	parcounter = 0
	lookAheadCounter = 0
	caller = ''
	Mips.append('L0:')
	Mips.append('j Lmain')
	
	for qk in quads:
		quad = quads[qk]
		Mips.append('L'+str(qk)+':')
		#print('L'+str(qk)+':')
		
		if quad[0] == 'begin_block':
			functioname = quad[1]
			if symbolTable[functioname][3] == functioname:
				Mips[-1] = 'Lmain:'
				framelength = symbolTable[functioname][1]
				Mips.append('addi $sp, $sp,'+str(framelength))
			else:
				Mips.append('sw $ra,-0($sp)')
			
		elif quad[0] == 'end_block':
			Mips.append('lw $ra,-0($sp)')
			Mips.append('jr $ra')
			
		elif quad[0] == 'jump':
			Mips.append('j '+'L'+str(quad[3]))		#### j or b ????
		
		elif quad[0] in relational_op:
			x = quad[1]
			y = quad[2]
			z = quad[3]
			
			if loadvr(x,'$t1',functioname) == 'ERROR':
				return 'ERROR'
			if loadvr(y,'$t2',functioname) == 'ERROR':
				return 'ERROR'
			
			if quad[0] == '=':
				Mips.append('beq $t1, $t2, L'+str(z))
			elif quad[0] == '<':
				Mips.append('blt $t1, $t2, L'+str(z))
			elif quad[0] == '>':
				Mips.append('bgt $t1, $t2, L'+str(z))
			elif quad[0] == '<>':
				Mips.append('bne $t1, $t2, L'+str(z))
			elif quad[0] == '<=':
				Mips.append('ble $t1, $t2, L'+str(z))
			elif quad[0] == '>=':
				Mips.append('bge $t1, $t2, L'+str(z))
			else:
				print('Error in finalcode relop')
				return 'ERROR'
		
		elif quad[0] == ':=':
			x = quad[1]
			z = quad[3]
			if loadvr(x,'$t1',functioname) == 'ERROR':
				print('In function ' + functioname + ', variable ' + x + ' is not declared.')
				return 'ERROR'
			if storerv('$t1',z,functioname) == 'ERROR':
				print('In function ' + functioname + ', variable ' + z + ' is not declared.')
				return "ERROR"
		
		elif quad[0] in ['+','-','*','/']:
			x = quad[1]
			y = quad[2]
			z = quad[3]

			if loadvr(x,'$t1',functioname) == 'ERROR':
				return 'ERROR'
			if loadvr(y,'$t2',functioname) == 'ERROR':
				return 'ERROR'
			
			if quad[0] == '+':
				Mips.append('add $t1, $t1, $t2')
			elif quad[0] == '-':
				Mips.append('sub $t1, $t1, $t2')
			elif quad[0] == '*':
				Mips.append('mul $t1, $t1, $t2')
			elif quad[0] == '/':
				Mips.append('div $t1, $t1, $t2')
				
			if storerv('$t1',z,functioname) == 'ERROR':
				return 'ERROR'
		
		elif quad[0] == 'out':
			x = quad[1]
			Mips.append('li $v0, 1')
			if loadvr(x,'$a0',functioname) == 'ERROR':
				return 'ERROR'
			Mips.append('syscall')
			
		elif quad[0] == 'inp':
			x = quad[1]
			Mips.append('li $v0, 5')
			Mips.append('syscall')
			if storerv('$v0',x,functioname) == 'ERROR':
				return 'ERROR'
		
		elif quad[0] == 'retv':
			x = quad[1]
			if loadvr(x,'$t1',functioname) == 'ERROR':
				return 'ERROR'
			Mips.append('lw $t0, -8($sp)')
			Mips.append('sw $t1, -0($t0)')
			Mips.append('lw $ra,-0($sp)')
			Mips.append('jr $ra')
			
		elif quad[0] == 'par':
			x = quad[1]
			parcounter += 1
			
			if parflag == 0:
				lookAheadCounter = int(qk)				
				while(True):
					lookAheadCounter += 1
					lookAheadQuad = quads[lookAheadCounter]
					if lookAheadQuad[0] == 'call':
						caller = functioname
						functioname = lookAheadQuad[1]						
						break
				
				parflag = 1		
				framelength = symbolTable.get(functioname)[1]
				Mips.append('addi $fp, $sp,'+str(framelength))	

			if quad[2] == 'CV':
				if loadvr(x,'$t0',functioname)	== 'ERROR':
					return 'ERROR'
				offset = 12 + 4*(parcounter-1)
				Mips.append('sw $t0,-'+str(offset)+'($fp)')
			
			elif quad[2] == 'REF':				
				depth1 = symbolTable.get(caller)[0]
				depth2 = symbolTable.get(functioname)[0]
				offset = -1
				offset1 = 12 + 4*(parcounter-1)
				
				if x in symbolTable.get(caller)[2]: #depth1 == depth2:

					variabledict = symbolTable.get(caller)[2]
					variablelist = variabledict[x]

					offset = variablelist[0]
					if len(variablelist) == 2 and variablelist[1] == 'REF':				
						Mips.append('lw $t0,-'+str(offset)+'($sp)')						
						Mips.append('sw $t0,-'+str(offset1)+'($fp)')
					else:
						Mips.append('addi $t0,$sp,-'+str(offset))
						Mips.append('sw $t0,-'+str(offset1)+'($fp)')
						
				elif x not in symbolTable.get(caller)[2]:  #depth1 < depth2:
					
					gnvl = gnvlcode(x,caller)

					if gnvl == 'ERROR':
						return 'ERROR'

					variabledict = symbolTable.get(gnvl)[2]
					variablelist = variabledict[x]
					
					if len(variablelist) == 2 and variablelist[1] == 'REF':						
						Mips.append('lw $t0, -0($t0)')
						Mips.append('sw $t0,-'+str(offset1)+'($fp)')
					else:
						Mips.append('sw $t0,-'+str(offset1)+'($fp)')
					
				else:
					print('Error finalcode par REF')
					return 'ERROR'
			
			elif quad[2] == 'RET':
				
				offset = symbolTable.get(caller)[2].get(quad[1])[0]
				Mips.append('addi $t0,$sp,-'+str(offset))
				Mips.append('sw $t0,-8($fp)')
		

		elif quad[0] == 'call':
			if parflag == 0:
				caller = functioname
				functioname = quad[1]
				framelength = symbolTable.get(functioname)[1]
				Mips.append('addi $fp, $sp,'+str(framelength))

			framelength = symbolTable.get(functioname)[1]
			
			depth1 = symbolTable.get(caller)[0]
			depth2 = symbolTable.get(functioname)[0]

			if depth1 < depth2 and not(depth2-1 == depth1):
				print('Subprogram \'' + caller + '\' can not call \'' + functioname +'\'')
				return 'ERROR'  
			
			parflag = 0
			parcounter = 0
			
			startquad = symbolTable.get(functioname)[4]
			
			if depth1 == depth2:
				Mips.append('lw $t0,-4($sp)')
				Mips.append('sw $t0,-4($fp)')
			elif depth1 != depth2: 
				Mips.append('sw $sp,-4($fp)')
			else:
				print('Error finalcode call')
				return 'ERROR'
			
			Mips.append('addi $sp, $sp,'+str(framelength))
			Mips.append('jal L'+str(startquad))
			Mips.append('addi $sp, $sp,-'+str(framelength))
			
			functioname = caller
			
	return "Final is correct"


token = lex()
programIsOk = program()
finalIsOk = finalcode()


if programIsOk == "Compile is correct" and finalIsOk == "Final is correct":
	print(programIsOk)

	output1 = open("intermediate_code.int", "w")
	
	output1.write('QUADS:\n')
	for i in quads:
		output1.write(str(i) +': '+ str(quads[i]) + '\n')

	output1.write('\nSYMBOL TABLE:\n')

	for fname in symbolTable:
		key = symbolTable.get(fname)
		output1.write(str(fname) + " " + str(key[0]) + " " + str(key[1]) + " " + str(key[2]) + " " + str(key[3]) + " " + str(key[4]) + '\n')			
	output1.close()

	output2 = open("final_code.asm", "w")
	for inst in Mips:
		output2.write(inst+'\n')
	output2.close()
	print('\nCreated intermediate_code.int and final_code.asm files')
