//DLMLPR0 JOB ($CSEN),RESTART=*,
//            NOTIFY=&SYSUID,REGION=0M,
//            CLASS=Y,MSGCLASS=X,MSGLEVEL=(1,1)
/*ROUTE XEQ   NJELPR0
//DLMSCR  EXEC PGM=DLMSCR,PARM='DEV=0102,TYPE=RMMDV,NODATECHK,NODSNCHK'
//STEPLIB  DD  DISP=SHR,DSN=S$PRD8.EMC.V240.LINKLIB
//DLMLOG   DD  SYSOUT=*
//DLMSCR   DD  *
  RMM DV Y01559 FORCE
