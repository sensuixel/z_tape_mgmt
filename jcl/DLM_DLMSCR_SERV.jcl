//DLMSERV JOB ($CSEN),RESTART=*,
//            NOTIFY=&SYSUID,REGION=0M,
//            CLASS=Y,MSGCLASS=X,MSGLEVEL=(1,1)
/*ROUTE XEQ   AGRRSERV
//DLMSCR  EXEC PGM=DLMSCR,PARM='DEV=0102,TYPE=RMMDV,NODATECHK,NODSNCHK'
//STEPLIB  DD  DISP=SHR,DSN=S$PRD8.EMC.V240.LINKLIB
//DLMLOG   DD  SYSOUT=*
//DLMSCR   DD  *
  RMM DV Q07894 FORCE
  RMM DV Q07896 FORCE
  RMM DV Q07924 FORCE
  RMM DV Q08269 FORCE
  RMM DV Q08281 FORCE
  RMM DV Q08509 FORCE
  RMM DV Q08529 FORCE
  RMM DV Q08855 FORCE
  RMM DV Q08905 FORCE
  RMM DV Q09302 FORCE
  RMM DV Q09329 FORCE
  RMM DV Q13873 FORCE
  RMM DV Q13899 FORCE
  RMM DV Q13913 FORCE
  RMM DV Q14063 FORCE
  RMM DV Q14136 FORCE
  RMM DV Q14563 FORCE
  RMM DV Q14574 FORCE
