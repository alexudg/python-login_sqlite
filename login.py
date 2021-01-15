import tkinter as tk
from tkinter import Menu, ttk, messagebox, filedialog#, simpledialog, commondialog
import configparser, os
import sqlite3
from tkinter.constants import END

isAdmin = False

class MenuMain(tk.Menu):
    def __init__(self, master): # master=root
        super().__init__(master)
        self.master = master # quedarse con root
        # my user
        self.menuMyUser = tk.Menu(self, tearoff=0) # menu dentro del menu principal, tearoff=linea punteada horizontal
        self.menuMyUser.add_command(label="Cerrar sesión", command=self.closeSession)
        self.add_cascade(label="Mi usuario", menu=self.menuMyUser)

    def closeSession(self):
        print('closeSession')
        self.finput = Input(self.master) # master=root        

class Input(tk.Toplevel):
    def __init__(self, master=None):
        super().__init__(master) #master=fmain
        # eliminar menu
        master.master.config(menu='') # master.master = root
        self.master = master
        self.withdraw() # ocultar para que no se vea el parpadeo
        self.iconbitmap('./favicon.ico')
        self.title('Ingreso de usuario')
        self.width, self.height = 300, 260
        self.s_width, self.s_height = self.winfo_screenwidth(), self.winfo_screenheight()        
        self.geometry('%dx%d+%d+%d' % (self.width, self.height, (self.s_width - self.width) / 2, (self.s_height - self.height) / 2))
        self.resizable(False, False)        
        self.attributes('-toolwindow', True) # sin botones de control
        ''' .attributes('<attrib>', <value>)
        -alpha
        -transparentcolor
        -disabled
        -fullscreen
        -toolwindow
        -topmost
        '''
        #self.overrideredirect(1) # sin barra de titulo 
        self.deiconify() # volver a mostrar para evitar que se viera el parpadeo
        self.grab_set() # deshabilitar al padre y poner la escucha de eventos a esta ventana
        self.createWidgets()
        self.protocol('WM_DELETE_WINDOW', root.destroy)

    def createWidgets(self):
        #print('createWidgets')
        tk.Label(self, text='Usuario:').place(x=30, y=20)
        self.enUser = ttk.Entry(self)
        self.enUser.place(x=120, y=20)
        self.enUser.bind('<Return>', self.btOkClick)
        tk.Label(self, text='Contraseña:').place(x=30, y=50)
        self.enPass = ttk.Entry(self, show='*')
        self.enPass.place(x=120, y=50)
        self.enPass.bind('<Return>', self.btOkClick)
        ttk.Button(self, text='Aceptar', command=self.btOkClick).place(x=50, y=100)
        ttk.Button(self, text='Cancelar', command=root.destroy).place(x=170, y=100)
        self.lf = ttk.LabelFrame(self, text='Base de datos')
        self.lf.place(x=20, y=150, width=260, height=100)
        tk.Label(self.lf, text='Ruta:').place(x=10, y=0)
        self.enPath = ttk.Entry(self.lf)
        self.enPath.place(x=10, y=20, width=210)

        ### leer archivo ini
        # [DATABASE]
        # path='<path>'
        self.iniFile = configparser.ConfigParser()
        if not os.path.isfile('data.ini'):
            print('no existe ini')
            self.iniFile.add_section('DATABASE')
            self.iniFile.set('DATABASE', 'path', os.getcwd() + '\database.db')            
            fp = open('data.ini','w')
            self.iniFile.write(fp)
            fp.close()
        
        self.iniFile.read('data.ini')
        #print(self.iniFile.get('DATABASE', 'path'))
        self.enPath.insert(0, self.iniFile.get('DATABASE', 'path'))

        ttk.Button(self.lf, text='...', command=self.btOpenDbClick).place(x=220, y=18, width=25)
        ttk.Button(self.lf, text='Prueba de conexión', command=self.btTestClick).place(x=70, y=50)
        self.enUser.focus()

    def btOkClick(self, event=None):
        #print(event)
        if len(self.enUser.get()) > 0:
            #print('user text exists')            
            if self.isDbConnected():
                ### import bcrypt
                # password = 'admin'
                # passHash = bcrypt.hashpw(password.encode(), bcrypt.gensalt())
                # print(passHash)
                # print(len(passHash))
                # valid = bcrypt.checkpw(password.encode(), passHash)
                # print(valid)
                # pass=''      $2b$12$.ut2v6VejU9PqVbCM.SVyuwBf9rjT/Ui2HN5f2NZ4QbK8Hd8JyIE2
                # pass='admin' $2b$12$k8TGieJH/Gu06fDOVRJM0.j154ER7sCDvhOkI/hBBAepiYLaZUX/y
                self.conn = sqlite3.connect(self.enPath.get())
                self.c = self.conn.cursor()
                self.sql = 'SELECT id FROM users WHERE UPPER(name) = ? AND pass = ?'
                self.params = (self.enUser.get().upper(), self.enPass.get())
                self.enPass.delete(0, END)
                self.c.execute(self.sql, self.params)
                self.result = self.c.fetchone() # tupla
                print(self.result)
                if self.result != None:
                    # si es administrador crear menu
                    if self.result[0] == 1:
                        self.master.master.config(menu=MenuMain(self.master)) # master.master=root
                    self.destroy()                    
                else:
                    messagebox.showerror('Error', 'Usuario o contraseña incorrecta') 
        else:
            messagebox.showerror('Error', 'Usuario vacío')
            self.enUser.focus()

    def btOpenDbClick(self):
        #print('btOpenDbClick')
        self.fileName = filedialog.askopenfilename()
        print(self.fileName)
        if self.fileName != '':
            self.enPath.delete(0, END)
            self.enPath.insert(0, self.fileName)

    def btTestClick(self):
        if self.isDbConnected():
            messagebox.showinfo('Base de datos', 'Conexion exitosa con la base de datos')    

    def isDbConnected(self):
        print('btTestClick')
        if os.path.isfile(self.enPath.get()):
            try:
                self.conn = sqlite3.connect(self.enPath.get())
                self.conn = None
                
                # conexion exitosa, guardar path
                self.iniFile = configparser.ConfigParser()
                self.iniFile.read('data.ini')
                self.iniFile.set('DATABASE', 'path', self.enPath.get())
                with open('data.ini', 'w') as fp:    # save
                    self.iniFile.write(fp)            
                return True
            except:
                messagebox.showerror('Base de datos', 'Error de conexion con la base de datos')
                return False
        else:
            messagebox.showerror('Base de datos', 'Error de conexion con la base de datos')
            return False

class Main(tk.Frame): # hereda de Frame
    def __init__(self, master=None): # recibe a root
        super().__init__(master)
        self.master = master # tomar a root 
        self.pack() # integrar el Frame en el root
        self.createWidgets()

    def createWidgets(self):
        self.master.withdraw() # ocultar ventana para evitar el 1er parpadeo de su creacion
        self.master.iconbitmap('./favicon.ico')
        self.master.title('Principal')
        
        # dimensiones y centrado inicial
        self.width, self.height = 600, 400
        self.s_width, self.s_height = self.winfo_screenwidth(), self.winfo_screenheight()
        self.master.geometry('%dx%d+%d+%d' % (self.width, self.height, (self.s_width - self.width) / 2, (self.s_height - self.height) / 2))

        # # menu
        # self.menuMain = tk.Menu(self.master) # master=root
        # self.master.config(menu=self.menuMain)
        # # menu mi usuario
        # self.menuMyUser = tk.Menu(self.menuMain, tearoff=0) # menu dentro del menu principal, tearoff=linea punteada horizontal
        # #self.menuMyUser.add_command(label="Cerrar sesión", command=self.btSessionClick)
        # self.menuMain.add_cascade(label="Mi usuario", menu=self.menuMyUser)

        self.master.deiconify() # mostrar ventana antes de maximizar para que alcance a centrarse
        #self.master.state('zoomed') # maximizar        

        ttk.Button(self, text='Cerrar sessión', command=self.btSessionClick).pack()
        self.btSessionClick()     

    def btSessionClick(self):
        #print('btSessionClick')
        self.finput = Input(self)                

root = tk.Tk()
fmain = Main(root)

root.mainloop()