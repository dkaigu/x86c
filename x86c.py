#############################################################################
#############################################################################
#########x86c.py - PYTHON SCRIPT FOR GENERATING x86##########################
#########          TESTS, BEHAVIORAL AND LOAD CONFIGURATIONS#################
#########AUTHOR:   IVANOV ALEXANDER V.             ##########################
#########VERSION:  0.6.2 with GUI                    ##########################
#############################################################################
import subprocess, os, sys, re, threading
from tkinter import Tk, Label, Button, Entry, Radiobutton, BooleanVar
##############################################################################
######PLEASE CHECK AND EDIT THESE PARAMS:

DEBUG_MODE             = False          #If False -> exit from dosbox after compile;
                                        #Set True if you want to see tasm debug info
DOSBOX_PATH            = r'M:\Program Files (x86)\DOSBox-0.74' #DosBox path
TOOLSN_PATH            = 'toolsn'                             #toolsn path
LOG_FILENAME           = 'log.log'
LISTING_SAVE_PATH      = 'lst'
TEST_SAVE_PATH         = 'tst'
EXE_SAVE_PATH          = 'exe'
LOG_SAVE_PATH          = 'log'
DOSBOX_CONFIG_FILENAME = 'db14356789.conf'
#Files list exeption for -a key; In lower case!!!!!!!!!!
EXCEPTION_FILES_LIST   = ['eth_ni.asm','pcbcore.asm','pcbsbg.asm','pcbdma.asm','pcbkm.asm','pcbicu.asm']
######RESERVED FILENAMES, ALL BE GENERATED AND DELETED IN PROCESS:
RESERVED_FILES = ['monit.asm','monit.obj','monit.map','monit.lst',
                  'monit.exe','monit.bin','myfile.xxx','vhdl.txt','vhdl.tst','stderr.txt',
                  'stdout.txt', LOG_FILENAME,DOSBOX_CONFIG_FILENAME]
USAGE_GUIDE = '''
x86c.py arg1[OPTIONAL] arg2[OPTIONAL] testname[FULL TESTNAME WITH EXTENSION]\n
arg1,arg1 - or/and:
by default tests is generating for behavioral configuration
-l(/l) - generate tests for load configuration
-a(/a) - compile all files in current folder
'''
############################################
############################################
############################################

my_env = os.environ.copy()
my_env['PATH'] = os.pathsep.join([DOSBOX_PATH, my_env['PATH']])
load_sequence = False
compile_all_infolder = False
console_mode = True
mount_dir = os.getcwd()
tasm_prog = os.path.join(TOOLSN_PATH,'tasm')
link_prog = os.path.join(TOOLSN_PATH,'tlink')
cutfile_prog = os.path.join(TOOLSN_PATH,'cutfile')
asnvhdl_prog = os.path.join(TOOLSN_PATH,'asnvhdl')
zerodel_prog = os.path.join(TOOLSN_PATH,'zerodel')
cuthead_prog = os.path.join(TOOLSN_PATH,'cuthead')
bin2tst_prog = os.path.join(TOOLSN_PATH,'bin2tst')
#create folders if not exist
def makefolders(load_sequence=False):
    if not os.path.exists(LISTING_SAVE_PATH):
        os.mkdir(LISTING_SAVE_PATH)
    if not os.path.exists(TEST_SAVE_PATH):
        os.mkdir(TEST_SAVE_PATH)    
    if not os.path.exists(LOG_SAVE_PATH):
        os.mkdir(LOG_SAVE_PATH)  
    if not os.path.exists(EXE_SAVE_PATH) and load_sequence == True:
        os.mkdir(EXE_SAVE_PATH)
    

def dosbox_compile(file_to_compile,load_sequence, DEBUG_MODE=False):
    file_to_compile_noext = (re.findall(r'(.*)\.',file_to_compile))[0]
    os.popen('copy '+file_to_compile+' monit.asm')

    if os.path.exists(LOG_FILENAME): os.remove(LOG_FILENAME)

    with open(DOSBOX_CONFIG_FILENAME,'w') as dosbox_config_file:
        dosbox_config_file.write('[autoexec]\n'+ 'mount c ' + mount_dir + '\nc:\n')
        if load_sequence == False:
            dosbox_config_file.write(tasm_prog+' '+'monit.asm'+' /zi/l >> '+LOG_FILENAME+'\n')
            dosbox_config_file.write(link_prog+' monit.obj'+' /l/v >> '+LOG_FILENAME+'\n')
            dosbox_config_file.write(cutfile_prog+' >> '+LOG_FILENAME+'\n')
            dosbox_config_file.write(asnvhdl_prog+' MYFILE.XXX FE000 >> '+LOG_FILENAME+'\n')
            dosbox_config_file.write(zerodel_prog+' vhdl.txt vhdl.tst >> '+LOG_FILENAME+'\n')
        else:
            dosbox_config_file.write(tasm_prog+'/s/m/t'+' monit.asm >> '+LOG_FILENAME+'\n')
            dosbox_config_file.write(link_prog+'/x monit >> '+LOG_FILENAME+'\n')
            dosbox_config_file.write(tasm_prog+' monit /l >> '+LOG_FILENAME+'\n')
            dosbox_config_file.write(cuthead_prog+' monit.exe monit.bin >> '+LOG_FILENAME+'\n')
            dosbox_config_file.write(bin2tst_prog+' monit.bin vhdl.tst >> '+LOG_FILENAME+'\n')
        if DEBUG_MODE == False:
            dosbox_config_file.write('exit')

    #result = subprocess.call('dosbox.exe','-conf db.conf', '-noconsole')
    subprocess.run(r'dosbox.exe -noconsole -conf '+ DOSBOX_CONFIG_FILENAME, env = my_env, shell = True)

    tst_filepath = os.path.join(TEST_SAVE_PATH, file_to_compile_noext+ '.tst') 
    lst_filepath = os.path.join(LISTING_SAVE_PATH, file_to_compile_noext+ '.lst') 
    exe_filepath = os.path.join(EXE_SAVE_PATH, file_to_compile_noext+ '.exe') 
    log_filepath = os.path.join(LOG_SAVE_PATH, file_to_compile_noext+ '.log') 
    if os.path.exists('vhdl.tst') and os.path.exists('MONIT.LST') and ((load_sequence == True and os.path.exists('MONIT.EXE')) or load_sequence == False):
        if os.path.exists(tst_filepath):os.remove(tst_filepath)
        if os.path.exists(lst_filepath): os.remove(lst_filepath)
        if os.path.exists(log_filepath): os.remove(log_filepath)
        if os.path.exists(exe_filepath) and load_sequence == True: os.remove(exe_filepath)
        os.rename('VHDL.TST', tst_filepath)
        os.rename('MONIT.LST', lst_filepath)
        os.rename(LOG_FILENAME, log_filepath)
        if load_sequence == True: os.rename('MONIT.EXE', exe_filepath)
        print('{:40} compile success'.format(file_to_compile))
    else:
        print('{:40} compile failed!!!'.format(file_to_compile))

    if os.path.exists(DOSBOX_CONFIG_FILENAME):
        os.remove(DOSBOX_CONFIG_FILENAME)
    else:
        print('Falied to delete doxbox config file, file not exist')
    del_file_list = ['monit.asm','MONIT.OBJ','MONIT.MAP','MONIT.LST','monit.exe','MONIT.BIN',
    'MYFILE.XXX','VHDL.TXT','VHDL.TST','stderr.txt','stdout.txt']
    for file in del_file_list:
        if os.path.exists(file): os.remove(file)
##########################################END OF FUNCTION
class App:
    def __init__(self, master):
        super().__init__()
        self.label_file_path = Label(master, text = 'Filename:')
        self.r_var = BooleanVar()
        self.r_var.set(0)
        self.radiobox_beh = Radiobutton(master, text = 'Behavioral', variable = self.r_var, value =0)
        self.radiobox_load = Radiobutton(master, text = 'Load', variable = self.r_var, value = 1)
        self.input_file_path = Entry(master, width=40)
        self.input_file_path.insert(0,'filename.asm')

        self.button_comp = Button(master, text='Compile', background="#DDD", command = lambda:self.Compile_click(self.input_file_path.get(),self.r_var))
        self.button_comp_all = Button(master, text='Compile all',background="#DDD", command = lambda:self.Compile_all_click(self.r_var),)
        self.label_file_path.grid(row=0,column=0, pady=10)
        self.input_file_path.grid(row=0,column=1, pady=10, padx=10)
        self.radiobox_beh.grid(row=1,column=0, pady=10)
        self.radiobox_load.grid(row=1,column=1, pady=10)
        self.button_comp.grid(row=2,column=0, pady=10)
        self.button_comp_all.grid(row=3,column=0, pady=10)


    def Compile_click(self, file_to_compile, r_var):
        if not check_for_resfiles(): return 1

        if r_var.get() == 0:
            load_sequence = False
        else:
            load_sequence = True
        makefolders(load_sequence)
        dosbox_compile(file_to_compile,load_sequence, DEBUG_MODE)

    def Compile_all_click(self, r_var):
        if not check_for_resfiles(): return 1
        files_list = os.listdir()
        if r_var.get() == 0:
            load_sequence = False
        else:
            load_sequence = True
        makefolders(load_sequence)
        for f in files_list:
            f = f.lower()
            if f.endswith('.asm') and f not in EXCEPTION_FILES_LIST:
                dosbox_compile(f, load_sequence)
    

def check_for_resfiles():
    files_list = os.listdir()
    for r in files_list:
        if r.lower() in RESERVED_FILES:
            print('Please check and delete RESERVED_FILES')
            print('Please remove file: ', r.lower())
            return False
    return True

if len(sys.argv) == 1:
    print('No arguments specified! Starting Gui\n',USAGE_GUIDE)

    root = Tk()
    myguy = App(root)
    root.mainloop()

    console_mode = False
elif len(sys.argv) in range(2,5):
    if not check_for_resfiles():
        exit(1)
    for i,arg in enumerate(sys.argv):
        if i == 0:continue
        if arg == '-l' or arg == '/l': load_sequence = True
        if arg == '-a' or arg == '/a': compile_all_infolder = True

    if compile_all_infolder == False:
        file_to_compile = sys.argv[len(sys.argv)-1]
    if compile_all_infolder == False and not os.path.exists(file_to_compile):
        print('File to compile not exist!\n',USAGE_GUIDE)
        exit(1)
else:
    print('Too much arguments!\n',USAGE_GUIDE)
    exit(1)

if console_mode == True:
    makefolders(load_sequence)
    if compile_all_infolder == True:
        files_list = os.listdir()
        for f in files_list:
            f = f.lower()
            if f.endswith('.asm') and f not in EXCEPTION_FILES_LIST:
                dosbox_compile(f, load_sequence)
    else:    
        dosbox_compile(file_to_compile, load_sequence, DEBUG_MODE)
