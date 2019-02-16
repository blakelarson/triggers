import datetime, json, notification, sqlite3, ui

'''
on open:
	- check to see if data already entered today
		- if not, start on entry screen
		- if so, then display results of past month, etc.
		
Try these ratings:
	0: unrated. maybe -1 or None so it isnt counted?
	1: bad. red light
	2: ok. yellow light
	3: good. green light
	

'''

def schedule_notfications():
	nots = notification.get_scheduled()
	#print(nots)
	dayrange = list(range(7))
	
	#print('dayrange before: {}'.format(dayrange))
	today = datetime.datetime.now()
	'''
	for n in nots:
		d1 = datetime.datetime.fromtimestamp( n['fire_date'] )
		diff = d1 - today
		#print('diff: {}'.format(diff.days ))
		if diff.days in dayrange:
			dayrange.remove(diff.days)
	print('dayrange after: {}'.format(dayrange))
	'''
		
		
	notification.cancel_all()

	for i in dayrange:
		day = today + datetime.timedelta(days=i)
		h = 21
		m = 30
	
		desired_time = day.replace(hour=h, minute=m, second=0, microsecond=0)
		#print(desired_time)
		
		if desired_time > today:
			delta = desired_time - today
			delay_seconds = delta.total_seconds()

			notification.schedule('Complete Triggers', delay_seconds, 'default', 'pythonista3://triggers/enter-triggers.py?action=run&root=iCloud')

			#print('seconds delayed: {0}'.format(delay_seconds))
	
	#print(notification.get_scheduled())

class DailyQs( ui.View ):
	def __init__(self):
		self.filename = 'data.json'
		#self.db_conn = DB_Interface('DailyQs.db')
		#self.questions = self.get_questions()
		self.questions = {}
		self.todays_answers = {}
		self.answer_history = {}
		self.read_db()
						
		self.dv = ui.ScrollView(name='QuestionView')
		self.dv.title = datetime.date.today().strftime('%Y-%m-%d')
		self.dv.background_color = 'cyan'
		
		self.mv = ui.ScrollView(name='AnswerView')
		self.mv.background_color = 'pink'
		self.num_days = 30
		
		self.button_colors = ['red', '#ffdb00', 'green']
		
		self.name = 'Daily Questions'
		self.today = datetime.date.today()
		for i in self.questions.keys():
			#self.todays_answers[i] = (-1)
			l = ui.Label(name='q{0}'.format(i))
			l.text = self.questions[i]
			l.background_color = 'white'
			self.dv.add_subview(l)
			for c in self.button_colors:
				b = ui.Button(name='q{0},{1}'.format(i,c))
				b.background_color = 'white'
				b.title = ' '
				b.image = ui.Image('iob:ios7_circle_outline_256')
				b.tint_color = c
				b.font = ('<system-bold>', 48 )
				b.action = self.button_pressed
				self.mv.add_subview(b)
			for d in range(0, self.num_days):
				day = self.today - datetime.timedelta(days=d)
				d_text = day.strftime('%Y-%m-%d')
				a = ui.Label(name='q{0},d{1}'.format(i,d_text))				
				a.background_color = 'grey'
				if d_text in self.answer_history:
					#print('d_text: {} exists as {}'.format(d_text, self.answer_history[d_text]))
					if str(i) in self.answer_history[d_text]:
						rating = self.answer_history[d_text][str(i)]
						a.background_color = self.button_colors[rating]
				
				self.mv.add_subview(a)
		'''		
		if self.answer_history[d_text]:
					if self.answer_history[d_text][i]:
						rating = self.answer_history[d_text][i]
						a.background_color = self.button_colors[rating]'''
			
			
		self.background_color = 'white'	
		rb = ui.ButtonItem(title='>')
		self.dv.right_button_items = [rb]
		self.add_subview(self.dv)
		
		#for i in range(0,len(self.questions)):
		#	l = ui.Label(name='q{0}'.format(i))
		#	l.text = self.questions[i]
		#	l.background_color = 'white'
		#	self.mv.add_subview(l)
		self.datelabel = ui.Label(name='datelabel')
		self.datelabel.text = self.today.strftime('%Y-%m-%d')
		self.datelabel.font = ('<system-bold>', 14)
		self.mv.add_subview(self.datelabel)
		
		for d in range(0, self.num_days):
			day = self.today - datetime.timedelta(days=d)
			h = ui.Label(name='h{0}'.format(day.strftime('%Y-%m-%d')))
			h.text = day.strftime('%d')
			h.font = ('<system>', 10)
			self.mv.add_subview(h)
			
		self.dv.add_subview(self.mv)
		
		#tmp = self.load_data()
		#tmp['Answers'].append(self.get_answers())

	def layout(self):
		q_label_width = 100
		self.dv.width = self.width
		self.dv.height = self.height
		
		self.mv.width = self.width - q_label_width
		self.mv.height = self.height / 2
		mv_content_width = 32*3 + 20*30
		self.mv.content_size = (mv_content_width, self.mv.height)
		self.mv.x = q_label_width
		self.mv.y = 0
		dv_content_height = 64 + 32*len(self.questions)
		self.dv.content_size = (self.dv.width, dv_content_height)
		
		self.datelabel.alignment = ui.ALIGN_CENTER
		self.datelabel.x = 0
		self.datelabel.y = 0
		self.datelabel.width = 96	
		
		if self.width > self.height:
			right_margin = 30
		else:
			right_margin = 2
		x_tmp = 100
		for d in range(0,self.num_days):
			day = self.today - datetime.timedelta(days=d)
			ind = 'h{0}'.format(day.strftime('%Y-%m-%d'))
			self.mv[ind].x = x_tmp
			self.mv[ind].y = 0
			x_tmp = x_tmp + 20
		y_tmp = 64
		for i in self.questions.keys():
			x_tmp = 0
			self.dv['q{}'.format(i)].x = 5
			self.dv['q{}'.format(i)].width = q_label_width
			self.dv['q{}'.format(i)].height = 32
			self.dv['q{}'.format(i)].y = y_tmp
			y_tmp = y_tmp +1
			for c in self.button_colors:
				ind = 'q{0},{1}'.format(i,c)
				self.mv[ind].width = 30
				self.mv[ind].height = 30
				self.mv[ind].x = x_tmp
				self.mv[ind].y = y_tmp
				x_tmp = x_tmp + 32
			x_tmp = x_tmp + 1
			y_tmp = y_tmp + 7 
			for d in range(0,self.num_days):
				day = self.today - datetime.timedelta(days=d)
				ind = 'q{0},d{1}'.format(i,day.strftime('%Y-%m-%d'))
				self.mv[ind].x = x_tmp
				self.mv[ind].y = y_tmp
				self.mv[ind].width = 18
				self.mv[ind].height = 18
				x_tmp = x_tmp + 20
			#self.mv['q{}'.format(i)].x = 5
			#self.mv['q{}'.format(i)].width = x_tmp - 5
			#self.mv['q{}'.format(i)].height = 62
			#self.mv['q{}'.format(i)].y = y_tmp
			y_tmp = y_tmp + 32
		
			
	def will_close(self):
		#pass
		self.write_db()
		#self.db_conn.close()
		#print(self.answers)
		
	def read_db(self):
		conn = sqlite3.connect('DailyQs.db')
		with conn:
			tmp = conn.execute('SELECT rowid, question FROM questions WHERE enabled=1')
			for row in tmp:
				self.questions['{}'.format(row[0])] = row[1]
			tmp2 = conn.execute('SELECT rowid, * FROM answers')
			for row in tmp2:
				#print('answer: {}'.format(row))
				ds = row[2]
				if ds not in self.answer_history:
					self.answer_history[ds] = {}
				self.answer_history[ds][str(row[1])] = row[3]
			#print('answer_history: {}'.format(self.answer_history))
			tmp3 = conn.execute('SELECT * FROM answers WHERE rowid=? AND date=?',(4,'2019-02-09'))
			for row in tmp3:
				print('match: {}'.format(row))
			#conn.execute('''CREATE TABLE answers (date INTEGER NOT NULL, qid INTEGER NOT NULL, answer INTEGER NOT NULL)''')
			#conn.execute('''CREATE UNIQUE INDEX idx_date_q ON answers (date,qid)''')
			#conn.execute('DELETE FROM answers WHERE rowid = 11')
		#with conn:
			#conn.execute('''REPLACE INTO answers VALUES (4, '2019-02-10', 1)''')
		conn.close()
		
	def write_db(self):
		conn = sqlite3.connect('DailyQs.db')
		#print(self.todays_answers)
		with conn:
			for i in self.todays_answers.keys():
				# check to see if today has already been saved for each answer
				if self.todays_answers[i] != -1:
					conn.execute('INSERT OR REPLACE INTO answers VALUES (?,?,?)',(i,self.today,self.todays_answers[i]))
					print('{0}: {1}'.format(i,self.todays_answers[i]))
		conn.close()
		
	def button_pressed(self, sender):
		[sel_q_txt, sel_color] = sender.name.split(',')
		sel_q = int(sel_q_txt[1:])
		if sender.title == 'X':
			sender.title = ' '
			self.todays_answers.pop(str(sel_q))
		else:
			sender.title = 'X'
			sender.image = ui.Image('iob:ios7_circle_filled_256')
			self.todays_answers[str(sel_q)] = self.button_colors.index(sel_color)
			for c in self.button_colors:
				#print('color_test for {}'.format(c))
				if c != sel_color:
					#print('test passed for {}'.format(c))
					ind = 'q{0},{1}'.format(sel_q,c)
					#print('{}'.format(ind))
					self.mv[ind].title = ' '	
					self.mv[ind].image = ui.Image('iob:ios7_circle_outline_256')
		
	def get_questions(self):
		qs = []
		conn = sqlite3.connect('DailyQs.db')
		with conn:
			tmp = conn.execute('SELECT question FROM questions ')
			for row in tmp:
				qs.append( row[0])
		conn.close()
		return qs

if __name__ == '__main__':
	schedule_notfications()
	v = DailyQs()
	v.present('sheet')
	
'''	
class DB_Interface():
	def __init__(self, name=None):
		self.conn = None
		self.cursor = None
		
		if name:
			self.open(name)
	
	@ui.in_background
	def open(self, name):
		try:
			self.conn = sqlite3.connect(name)
			self.cursor = self.conn.cursor()
		except sqlite3.Error as e:
			print("Error connecting to database!")
			
	@ui.in_background
	def close(self):
		if self.conn:
			self.conn.commit()
			self.cursor.close()
			self.conn.close()
			
	def __enter__(self):
		return self
		
	def __exit__(self):
		self.close()
		
	@ui.in_background
	def get_questions(self):
		# just get a list of questoons in order
		qs = []
		with self.conn:
			tmp = self.conn.execute('SELECT question FROM questions ')
			for row in tmp:
				qs.append( row[0])
		return qs
		
	def save_answers(self, ans_list):
		# write array & date
		pass
		
	def get_answers(self, from_date, to_date):
		pass
	
current_questions = ['Exercise']
current_questions.append('Sleep')
tmp={'Current Questions': current_questions}	

	def load_data(self):
		pass
		#conn = sqlite3.connect('DailyQs.db')
		
		#c.execute('CREATE TABLE questions (question text, enabled integer)')
		#with conn:
		
		#	conn.execute("INSERT INTO questions VALUES ('Diet', 1)")
			#ds = int(datetime.datetime.now().timestamp())
			#ds = datetime.date.today().isoformat()
			#ds = datetime.date.today().strftime('%Y%m%d')
			#print(ds) 
			#ds2 = datetime.datetime.strptime(ds,'%Y%m%d')
			#print(ds2)
		#	conn.execute("INSERT INTO answers VALUES (1, ?, 1)", ds)
		
		#conn.close()
		#with open(self.filename,'r+') as f:
			#tmp = json.load(f, strict=False)
			#return tmp
			
'''
