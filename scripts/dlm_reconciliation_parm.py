# Paths
JCL_PATH = r'/usr/lpp/ag2r/dlm/reconciliation_v2/jcl'
CP503_PATH = r'/usr/lpp/ag2r/dlm/reconciliation'
OAM_PATH = r'/u/nfs/syspf/reconciliation'
CTT_PATH = r'/u/nfs/syspf/reconciliation'
REPORT_PATH = r'/u/nfs/syspf/job'

# Tape parameter
SCRATCH_CHAR = "~"

# Valid Media Type
VALID_MEDIA_TYPE = [ 'CRS',
                     'DLM',
                     ]

DRIVER_DLM = { 'DLM' : '0102',
               'CRS' : '0302',
               }

# ROUTEXEQ Dict
XEQ_Dict = { 'SERV' : 'AGRRSERV',
             'DEVE' : 'AGRRDEV ',
             'PROD' : 'AGRRNJE',
             'LPP0' : 'NJEPROD',
             'LPR0' : 'NJELPR0',
             'LPE0' : 'NJELPE0',
             'RECT' : 'AGRRRECT',
             'INFO' : 'AGRRREC',
             'XNET' : 'AGRRXNET',
             'SYSP' : 'AGRRSYSP',
             'SYST' : 'AGRRSYST',
             }

# JCL Parm
job_card = '''//DLM{} JOB ($CSEN),RESTART=*,
//            NOTIFY=&SYSUID,REGION=0M,
//            CLASS=Y,MSGCLASS=X,MSGLEVEL=(1,1)'''

xeq_card = '''/*ROUTE XEQ   {}'''

rmmdv_step = '''//DLMSCR  EXEC PGM=DLMSCR,PARM='DEV={},TYPE=RMMDV,NODATECHK,NODSNCHK'
//STEPLIB  DD  DISP=SHR,DSN=S$PRD8.EMC.V240.LINKLIB
//DLMLOG   DD  SYSOUT=*
//DLMSCR   DD  *'''

rmmdv_command = '''  RMM DV {} FORCE'''

alter_volent_step = '''//DEFINE   EXEC PGM=IDCAMS 
//SYSPRINT DD SYSOUT=*     
//SYSIN    DD *'''

alter_volent_command = ''' ALTER V{} VOLUMEENTRY USEATTRIBUTE(SCRATCH)'''

# HTML Parm
html_start = '''<!DOCTYPE html> 
<html> 
<head> 
    <title>{}</title> 
</head> 
 
<body> \n'''

html_end = '''	
</body> 
</html>
\n'''
